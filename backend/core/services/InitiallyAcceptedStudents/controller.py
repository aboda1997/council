import json
import re
from datetime import date

from django.core.cache import cache
from django.db import DatabaseError, transaction
from django.db.models import F, Subquery
from django.utils import timezone

from core.helpers.general import run_sql_command
from core.helpers.student_transactions import (
    create_path_shift_transaction,
    create_receive_transaction,
    create_withdraw_transaction,
)
from core.helpers.students import generate_student_unique_id, get_student_query
from core.models.db import (
    Certificates,
    Faculties,
    Gender,
    Regions,
    RegistrationType,
    Religion,
    SchoolType,
    Semesters,
    Stages,
    Students,
    StudentsAcceptedApplication,
    StudentsSecondaryEdu,
    StudentsTransactions,
    StudentsUniversityEdu,
    StudyGroups,
    Universities,
    Years,
)
from core.services.InitiallyAcceptedStudents.validation import ValidationRules
from core.utils.enums import (
    CountryEnum,
    ISODatePattern,
    NIDPattern,
    RegistrationTypeEnum,
    StudentStatus,
    TransactionsTypeEnum,
)
from core.utils.messages import SERVICE_MESSSAGES
from core.utils.validators import Validation


def add_student(students: list):
    """
    map student data and create four records for every student in the
    students list in database
        student data            >> students table
        student education data  >> studentssecondaryedu table
        student acceptance data >> studentsacceptedapplication table,
                                   studentsuniversityedu table
    Args:
        students (list): list of students every student has three dicts
    """

    council_ids_map = create_council_tables_map(get_council_tables())
    current_year_code, current_semester_code = current_year_semester()

    # format {"tansiqid": "str", "status": "str", "code": number, "message": "str", }
    results = []
    reserved_tansiq_ids = []

    for student_data in students:
        tansiqid = None
        if isinstance(student_data, dict) and "student" in student_data:
            tansiqid = student_data.get("student").get("id")

        # check if student_data is a dict contains the required three dictionaries
        result = check_data_format(student_data, tansiqid)
        if not result.get("success"):
            results.append(result.get("message"))
            continue

        # check if student has tansiqid
        if not tansiqid:
            results.append(
                generate_rejected_message(tansiqid, 31, "MISSING_STUDENT_ID")
            )
            continue

        # get data
        student_basic_data = student_data.get("student")
        education_data = student_data.get("studentEdu")
        acceptance_data = student_data.get("studentAcceptance")

        # map faculty id, do not accept student if faculty id does not exist
        faculty_id = acceptance_data.get("fac_id")
        mapped_faculty_id = council_ids_map.get("faculties").get(faculty_id)
        if not mapped_faculty_id:
            results.append(
                generate_rejected_message(
                    tansiqid,
                    31,
                    None,
                    SERVICE_MESSSAGES.get("INVALID_TANSIQ_ID").format(
                        dict="studentAcceptance", prop="fac_id"
                    ),
                )
            )
            continue

        if exists_in_current_ids(tansiqid):
            results.append(
                generate_rejected_message(tansiqid, 61, "STUDENT_IN_ANOTHER_REQUEST")
            )
            continue

        reserved_tansiq_ids.append(tansiqid)

        mapped_certificate_id = council_ids_map.get("certificates").get(
            education_data.get("studentSecondaryCert_id")
        )
        mapped_certificate_year_id = council_ids_map.get("years").get(
            education_data.get("year_id")
        )

        conditions: list = ["0", "0"]

        # try to find student by `tansiqid`, `national id`, `seat number`, or `passport`
        target_student = find_student(
            tansiqid,
            student_basic_data.get("studentNID"),
            education_data.get("studentSeatNumber"),
            education_data.get("studentPassport"),
            mapped_certificate_id,
            mapped_certificate_year_id,
            conditions,
        )

        result = check_action(
            tansiqid,
            target_student,
            mapped_faculty_id,
            current_year_code,
            current_semester_code,
            conditions,
        )
        if not result.get("success"):
            results.append({**result.get("message"), "case_code": "".join(conditions)})

        elif result.get("action") == "ignore":
            results.append(
                {
                    **generate_accepted_message(tansiqid, 11, "STUDENT_ALREADY_EXISTS"),
                    "case_code": "".join(conditions),
                }
            )

        elif result.get("action") in ["create", "update"]:
            message = create_or_update(
                student_data, target_student, tansiqid, council_ids_map
            )
            results.append({**message, "case_code": "".join(conditions)})

        elif result.get("action") in ["shift", "enroll"]:
            message = apply_path_shift_or_enroll(
                result.get("action"),
                target_student,
                acceptance_data,
                tansiqid,
                council_ids_map,
            )
            results.append({**message, "case_code": "".join(conditions)})

    remove_from_current_ids(reserved_tansiq_ids)

    return results


def create_or_update(student_data, target_student, tansiqid, council_ids_map):
    student_basic_data = student_data.get("student")
    education_data = student_data.get("studentEdu")
    acceptance_data = student_data.get("studentAcceptance")
    registration_type = acceptance_data.get("registrationType")

    # check nationality id
    result = check_student_nationality(
        student_basic_data, target_student, registration_type, tansiqid
    )
    if not result.get("success"):
        return result.get("message")

    # check student certificate id, total degree, and equivalent degree
    result = check_student_degree(education_data, tansiqid)
    if not result.get("success"):
        return result.get("message")

    result = check_student_name(student_basic_data, registration_type, tansiqid)
    if not result.get("success"):
        return result.get("message")

    # validate all fields
    validations = [
        *ValidationRules.student(student_basic_data),
        *ValidationRules.education_data(education_data),
        *ValidationRules.acceptance_data(acceptance_data),
    ]

    validation_result = Validation.run_validators_set(validations, True)

    if not validation_result.get("success"):
        return generate_rejected_message(tansiqid, 40, validation_result.get("message"))

    # generate unique id
    if target_student and target_student.get("uniqueId"):
        student_basic_data["uniqueId"] = target_student.get("uniqueId")
    else:
        student_basic_data["uniqueId"] = generate_student_unique_id()

    # format date
    birth_date = student_basic_data.get("studentBirthDate")
    if birth_date:
        formatted_birth_date = formate_date(birth_date, True)
        if formatted_birth_date:
            student_basic_data["studentBirthDate"] = formatted_birth_date
        else:
            return generate_rejected_message(tansiqid, 40, "INVALID_BIRTH_DATE_RANGE")

    created_at = acceptance_data.get("accept_createdAt")
    if created_at:
        acceptance_data["accept_createdAt"] = formate_date(created_at)

    # check and map all tansiq ids if exist in the council tables
    result = ValidationRules.validate_tansiq_ids(student_data, council_ids_map)
    if not result.get("success"):
        return generate_rejected_message(tansiqid, 50, None, result.get("message"))

    result = create_student_records(
        student_basic_data,
        education_data,
        acceptance_data,
        target_student,
        tansiqid,
    )
    return result.get("message")


def apply_path_shift_or_enroll(
    action, target_student, acceptance_data, tansiqid, council_ids_map
):
    # validate only university education data (data needed in path shift)
    validations = ValidationRules.acceptance_data(acceptance_data)
    validation_result = Validation.run_validators_set(validations, True)
    if not validation_result.get("success"):
        return generate_rejected_message(tansiqid, 40, validation_result.get("message"))

    created_at = acceptance_data.get("accept_createdAt")
    if created_at:
        acceptance_data["accept_createdAt"] = formate_date(created_at)

    # check and map all tansiq ids if exist in the council tables
    result = ValidationRules.validate_acceptance_data_tansiq_ids(
        acceptance_data, council_ids_map
    )
    if not result.get("success"):
        return generate_rejected_message(tansiqid, 50, None, result.get("message"))

    return update_university_education(
        action, target_student, acceptance_data, tansiqid
    )


def remove_student_records(students: list):
    """
    check if every tansiqId exist in the database and student
    status is initially accepted
    then remove the four records of the student in these tables
    students, studentssecondaryedu, studentsacceptedapplication,
    and studentsuniversityedu
    Args:
        students (list): list of tansiqIds
    """
    results = []

    for tansiqid in students:
        if not tansiqid:
            results.append(
                generate_rejected_message(tansiqid, 31, "MISSING_STUDENT_ID")
            )
            continue

        student_query = Students.objects.filter(tansiqid=tansiqid)
        target_student = student_query.values(
            "id", "studentStatus_id", "uniqueId"
        ).first()

        if not target_student:
            results.append(generate_rejected_message(tansiqid, 22, "STUDENT_NOT_FOUND"))
            continue

        if (
            target_student.get("studentStatus_id")
            != StudentStatus.INITIALLY_ACCEPTED.value
        ):
            results.append(
                generate_rejected_message(tansiqid, 11, "CANNOT_WITHDRAW_STUDENT")
            )
            continue

        # check if student has a path shift transaction
        path_shift_data = check_path_shift(target_student.get("uniqueId"))

        try:
            with transaction.atomic():
                if path_shift_data:
                    student_query.update(**path_shift_data.get("student_data"))

                    StudentsSecondaryEdu.objects.filter(
                        student_id=target_student.get("id")
                    ).update(**path_shift_data.get("secondary_data"))

                    StudentsUniversityEdu.objects.filter(
                        student_id=target_student.get("id")
                    ).update(**path_shift_data.get("university_data"))

                else:
                    student_query.delete()

                create_withdraw_transaction(target_student.get("uniqueId"), tansiqid)

                results.append(
                    generate_accepted_message(
                        tansiqid,
                        12,
                        "STUDENT_WITHDRAWN",
                    )
                )
        except DatabaseError:
            results.append(generate_rejected_message(tansiqid, 60, "UNEXPECTED_ERROR"))

    return results


def check_path_shift(unique_id):
    path_shift_transaction = (
        StudentsTransactions.objects.filter(
            uniqueId=unique_id, transactionType_id=TransactionsTypeEnum.PATH_SHIFT.value
        )
        .values("originalData")
        .order_by("-createdAt")
        .first()
    )

    if path_shift_transaction:
        current_date = timezone.now()
        original_data = json.loads(path_shift_transaction.get("originalData"))

        student_data = {
            "updatedAt": current_date,
            "updatedBy": 0,
            "studentStatus_id": original_data.get("Status_id"),
        }

        secondary_data = {
            "updatedAt": current_date,
            "updatedBy": 0,
        }

        university_data = {
            "updatedAt": current_date,
            "updatedBy": 0,
            "studentTot": original_data.get("Tot"),
            "studentFaculty_id": original_data.get("Faculty_id"),
            "studentUniveristy_id": original_data.get("Univeristy_id"),
            "studentEnrollYear_id": original_data.get("EnrollYear_id"),
            "studentEnrollSemester_id": original_data.get("EnrollSemester_id"),
            "studentEnrollStage_id": original_data.get("EnrollStage_id"),
        }
        if "pathShiftDate" in original_data:
            university_data["pathShiftDate"] = original_data.get("pathShiftDate")

        return {
            "student_data": student_data,
            "secondary_data": secondary_data,
            "university_data": university_data,
        }

    return None


def get_council_tables():
    return {
        "certificates": Certificates.objects.all().values("id", "tansiqid"),
        "faculties": Faculties.objects.all().values("id", "tansiqid", "univ_id"),
        "gender": Gender.objects.all().values("id", "tansiqid"),
        "regions": Regions.objects.filter(tansiqid__isnull=False).values(
            "id", "tansiqid"
        ),
        "religions": Religion.objects.all().values("id", "tansiqid"),
        "registrationtype": RegistrationType.objects.filter(
            tansiqid__isnull=False
        ).values("id", "tansiqid"),
        "schooltype": SchoolType.objects.all().values("id", "tansiqid"),
        "semesters": Semesters.objects.all().values("id", "tansiqid"),
        "stages": Stages.objects.all().values("id", "tansiqid"),
        "studygroups": StudyGroups.objects.all().values("id", "tansiqid"),
        "universities": Universities.objects.all().values("id", "tansiqid"),
        "years": Years.objects.all().values("id", "tansiqid"),
    }


def generate_accepted_message(tansiqid, code, service_message_key):
    return {
        "tansiqid": tansiqid,
        "status": "accepted",
        "code": code or 0,
        "message": SERVICE_MESSSAGES.get(service_message_key),
    }


def generate_rejected_message(
    tansiqid, code, service_message_key, additional_message=""
):
    message = (
        SERVICE_MESSSAGES.get(service_message_key) + additional_message
        if service_message_key
        else additional_message
    )
    return {
        "tansiqid": tansiqid,
        "status": "rejected",
        "code": code or 0,
        "message": message,
    }


def create_council_tables_map(council_tables: dict[str, any]):
    """
    create a dict for every table where the {key: value} is {tansiqid: id}
    """
    for table_name, table_records in council_tables.items():
        formatted_dict = {}
        for record in table_records:
            if record.get("tansiqid"):
                if "|" in record.get("tansiqid"):
                    ids = record.get("tansiqid").split("|")
                    for id in ids:
                        formatted_dict[id] = record.get("id")
                else:
                    formatted_dict[record.get("tansiqid")] = record.get("id")

        council_tables[table_name] = formatted_dict

    return council_tables


def check_data_format(student_data, tansiqid):
    if not isinstance(student_data, dict) or (
        "student" not in student_data
        or "studentEdu" not in student_data
        or "studentAcceptance" not in student_data
    ):
        return {
            "success": False,
            "message": generate_rejected_message(
                tansiqid, 21, "INVALID_STUDENT_FORMAT"
            ),
        }
    return {"success": True}


def find_student(
    tansiqid,
    national_id,
    seat_number,
    passport,
    certificate_id,
    certificate_year_id,
    conditions,
):
    values = [
        "id",
        "studentNID",
        "studentStatus_id",
        "university__pathShiftDate",
        "uniqueId",
    ]

    # find student by `tansiq id`
    student = Students.objects.filter(tansiqid=tansiqid).values(*values).first()
    if student:
        conditions[0] = "1"
        return student

    # if student not found by `tansiq id` try to find by `national id`
    if not student and national_id and isinstance(national_id, (int, str)):
        student = (
            Students.objects.filter(studentNID=national_id).values(*values).first()
        )
        if student:
            conditions[0] = "2"
            return student

    # if student not found by `national id`
    # try to find by `seat number` for only egyptian GS students
    if (
        not student
        and seat_number
        and certificate_id == 1  # `1` for egyptian GS students
        and certificate_year_id
        and isinstance(seat_number, (int, str))
    ):
        student = (
            Students.objects.filter(
                secondary__studentSeatNumber=seat_number,
                secondary__studentCertificateYear_id=certificate_year_id,
            )
            .values(*values)
            .first()
        )
        if student:
            conditions[0] = "3"
            return student

    # if student not found by `seat number` try to find by `passport`
    if not student and passport and isinstance(passport, (int, str)):
        student = (
            Students.objects.filter(studentPassport=passport).values(*values).first()
        )
        if student:
            conditions[0] = "4"
            return student

    conditions[0] = "5"
    return None


def check_action(
    tansiqid,
    target_student,
    mapped_faculty_id,
    current_year_code,
    current_semester_code,
    conditions,
):
    """
    check if the student exists and if need to apply path shift or enroll
        - `update` student if exists and (found by tansiqid) and status is `initially accepted`
        - `path shift` or `enroll` student if accepted in a pervious year
        - `ignore` student if accepted in the current year
        - `create` student if does not exist
    Args:
        tansiqid (int): student tansiqid
        target_student (Students): student object
        found_by (str): one of (tansiqid, national_id, or seat_number)
        mapped_faculty_id (int|str): mapped faculty id
    Returns:
        dict: return and action (need to be updated or apply `path shift` or `enroll`)
    """
    if not target_student:
        conditions[1] = "1"
        return {"success": True, "action": "create"}

    elif target_student:
        enroll_year_code, enroll_semester_code = enroll_year_semester(
            target_student.get("id")
        )
        student_status_id = target_student.get("studentStatus_id")
        if student_status_id == StudentStatus.INITIALLY_ACCEPTED.value:
            can_update_student = check_path_shift_date(target_student)
            if enroll_year_code and enroll_semester_code:
                if not can_update_student:
                    return {
                        "success": False,
                        "message": generate_rejected_message(
                            tansiqid, 25, "PATH_SHIFT_APPLIED"
                        ),
                    }
                elif (
                    enroll_year_code == current_year_code
                    and enroll_semester_code == current_semester_code
                ):
                    conditions[1] = "2"
                    return {"success": True, "action": "update"}

        elif student_status_id in [
            *StudentStatus.ACCEPTANCE_STATUS.value,
            StudentStatus.WITHDRAWN.value,
        ]:
            return check_path_shift_or_enroll(
                current_year_code,
                enroll_year_code,
                target_student,
                mapped_faculty_id,
                tansiqid,
                conditions,
            )

    conditions[1] = "7"
    return {"success": True, "action": "ignore"}


def check_path_shift_date(target_student):
    can_update = True
    path_shift_date: date = target_student.get("university__pathShiftDate")
    if not path_shift_date:
        return True

    today = date.today()
    diff = (today - path_shift_date).days

    # do not update student if path shift has been applied in the current semester
    # in the last 90 days (~3 months)
    if path_shift_date and diff < 90:
        can_update = False

    return can_update


def check_path_shift_or_enroll(
    current_year_code,
    enroll_year_code,
    target_student,
    mapped_faculty_id,
    tansiqid,
    conditions,
):
    """
    Args:
        student_id (int|str): student id
        mapped_faculty_id (int|str): mapped faculty id
    Returns:
        dict:
            - success (boolean)
            - action (str): one of `ignore`, `shift`, or `enroll`
            - message (str): message key of an error if occurred
    """
    # ----- check acceptance year -----

    accepted_in_previous_year = current_year_code != enroll_year_code

    if not accepted_in_previous_year:
        conditions[1] = "6"
        return {"success": True, "action": "ignore"}

    # ----- check faculty name -----

    faculty = (
        Faculties.objects.filter(id=mapped_faculty_id)
        .values("facultyname_id", "univ_id")
        .first()
    )

    student = (
        get_student_query(target_student.get("id"))
        .prefetch_related("university")
        .values(
            "university__studentFaculty_id",
            "university__studentFaculty__facultyname_id",
        )
        .first()
    )
    current_faculty_id = student.get("university__studentFaculty_id")
    current_faculty_name_id = student.get("university__studentFaculty__facultyname_id")

    is_withdrawn = (
        target_student.get("studentStatus_id") == StudentStatus.WITHDRAWN.value
    )

    if current_faculty_id == mapped_faculty_id:
        if is_withdrawn:
            conditions[1] = "3"
            return {"success": True, "action": "enroll"}
        else:
            return {
                "success": False,
                "message": generate_rejected_message(
                    tansiqid, 23, "STUDENT_ACCEPTED_PERVIOUS_YEAR"
                ),
            }

    # shift or enroll
    if faculty.get("facultyname_id") == current_faculty_name_id:
        if is_withdrawn:
            conditions[1] = "4"
            return {"success": True, "action": "enroll"}
        else:
            return {
                "success": False,
                "message": generate_rejected_message(
                    tansiqid, 24, "STUDENT_EXISTS_IN_ANOTHER_FACULTY"
                ),
            }
    else:
        conditions[1] = "5"
        return {"success": True, "action": "shift"}


def check_student_nationality(
    student_basic_data, target_student, registration_type, tansiqid
):
    nationality_id = student_basic_data.get("studentNationality_id")
    national_id = student_basic_data.get("studentNID")
    passport = student_basic_data.get("studentPassport")

    if not nationality_id:
        return {
            "success": False,
            "message": generate_rejected_message(
                tansiqid, 32, "MISSING_NATIONALITY_ID"
            ),
        }
    elif not str(nationality_id).isdigit():
        return {
            "success": False,
            "message": generate_rejected_message(tansiqid, 32, "INVALID_NATIONAL_ID"),
        }
    else:
        nationality_id = int(nationality_id)

    if nationality_id == CountryEnum.EGYPT.value and not national_id:
        # student national id is required for egyptian students
        return {
            "success": False,
            "message": generate_rejected_message(tansiqid, 33, "MISSING_NATIONAL_ID"),
        }
    elif (
        nationality_id != CountryEnum.EGYPT.value and not passport
    ):  # passport is required for non egyptian students
        return {
            "success": False,
            "message": generate_rejected_message(tansiqid, 34, "MISSING_PASSPORT"),
        }

    # national id must be unique
    if national_id:
        if not target_student or (
            target_student and str(national_id) != str(target_student.get("studentNID"))
        ):
            if Students.objects.filter(studentNID=national_id).exists():
                return {
                    "success": False,
                    "message": generate_rejected_message(
                        tansiqid, 30, "STUDENT_NATIONAL_ID_EXISTS"
                    ),
                }

        if str(registration_type) != "332":
            # `332` -> tansiqid for registration type = incoming students (الطلاب الوافدين)
            if len(national_id) != 14 or not re.search(NIDPattern, national_id):
                return {
                    "success": False,
                    "message": generate_rejected_message(
                        tansiqid, 40, "INVALID_NATIONAL_ID"
                    ),
                }

    return {"success": True}


def check_student_degree(education_data, tansiqid):
    # student total degree is required if (GS) student
    if not education_data.get("studentSecondaryCert_id"):
        return {
            "success": False,
            "message": generate_rejected_message(tansiqid, 35, "MISSING_CERT_ID"),
        }
    if str(education_data.get("studentSecondaryCert_id")) == "48":
        # "48" for general secondary students (GS)
        if not education_data.get("studentTot"):
            return {
                "success": False,
                "message": generate_rejected_message(
                    tansiqid, 36, "MISSING_TOTAL_DEGREE"
                ),
            }
    else:
        # student equivalent is required if non (GS) student
        if not education_data.get("studentEquivTotscienceB"):
            return {
                "success": False,
                "message": generate_rejected_message(
                    tansiqid, 37, "MISSING_EQUIV_DEGREE"
                ),
            }
    return {"success": True}


def check_student_name(student_basic_data, registration_type, tansiqid):
    student_name = student_basic_data.get("studentNameAr", "").strip()

    start_end_regex = r"^[^\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF]|[^\u0600-\u065F\u066A-\u06EF\u06FA-\u06FF]$"
    student_name = re.sub(start_end_regex, "", student_name)
    student_basic_data["studentNameAr"] = student_name

    name_parts = student_name.strip().split(" ")

    is_incoming_student = str(registration_type) == "332"

    # `332` -> tansiqid for registration type = incoming students (الطلاب الوافدين)
    if (is_incoming_student and len(name_parts) < 2) or (
        not is_incoming_student and len(name_parts) < 4
    ):
        return {
            "success": False,
            "message": generate_rejected_message(tansiqid, 40, "INVALID_STUDENT_NAME"),
        }

    return {"success": True}


def reformat_student_data(basic_data):
    formatted_data = {
        "createdBy": 0,
        "tansiqid": basic_data.get("id"),
        "studentName": basic_data.get("studentNameAr").strip() + "|",
        "studentStatus_id": StudentStatus.INITIALLY_ACCEPTED.value,
    }

    # map received to database
    attributes = [
        {"received": "studentNID", "database": "studentNID"},
        {"received": "studentPassport", "database": "studentPassport"},
        {"received": "studentPhone", "database": "studentPhone"},
        {"received": "studentMail", "database": "studentMail"},
        {"received": "studentAddress", "database": "studentAddress"},
        {"received": "studentBirthDate", "database": "studentBirthDate"},
        {"received": "uniqueId", "database": "uniqueId"},
        # Ids
        {"received": "studentAddressPlace_id", "database": "studentAddressPlaceGov_id"},
        {"received": "studentBirthPlace_id", "database": "studentBirthPlaceGov_id"},
        {"received": "studentGender_id", "database": "studentGender_id"},
        {"received": "studentNationality_id", "database": "studentNationality_id"},
        {"received": "studentReligion_id", "database": "studentReligion_id"},
    ]

    for attribute in attributes:
        received = basic_data.get(attribute.get("received"))
        if received:
            formatted_data[attribute.get("database")] = received

    return formatted_data


def reformat_education_data(education_data, student_id):
    formatted_data = {
        "createdBy": 0,
        "student_id": student_id,
    }

    # map received to database
    attributes = [
        {"received": "studentSchool", "database": "studentSchool"},
        {"received": "studentDept", "database": "studentDept"},
        {"received": "studentSeatNumber", "database": "studentSeatNumber"},
        {"received": "studentTot", "database": "studentTot"},
        {"received": "studentEquivTotscienceB", "database": "studentEquivTot"},
        {"received": "studentSportDegree", "database": "studentSportDegree"},
        {"received": "studentComplainGain", "database": "studentComplainGain"},
        # Ids
        {"received": "year_id", "database": "studentCertificateYear_id"},
        {"received": "studentDeptCode_id", "database": "studentDeptCode_id"},
        {"received": "studentCity_id", "database": "studentGov_id"},
        {"received": "studentSchoolType_id", "database": "studentSchoolType_id"},
        {"received": "studentSecondaryCert_id", "database": "studentSecondaryCert_id"},
        {"received": "studentSpecialization_id", "database": "studentStudyGroup_id"},
    ]

    for attribute in attributes:
        received = education_data.get(attribute.get("received"))
        if received:
            formatted_data[attribute.get("database")] = received

    return formatted_data


def reformat_acceptance_data(acceptance_data, student_id):
    formatted_data = {
        "createdBy": 0,
        "student_id": student_id,
    }

    # map received to database
    attributes = [
        {"received": "accept_studentTot", "database": "studentTot"},
        {"received": "manualAddition", "database": "manualAddition"},
        {"received": "createdAt", "database": "accept_createdAt"},
        # Ids
        {"received": "fac_id", "database": "fac_id"},
        {"received": "semester_id", "database": "semester_id"},
        {"received": "stage_id", "database": "stage_id"},
        {"received": "accept_year_id", "database": "year_id"},
    ]

    for attribute in attributes:
        received = acceptance_data.get(attribute.get("received"))
        if received:
            formatted_data[attribute.get("database")] = received

    return formatted_data


def reformat_university_data(acceptance_data, student_id, student_exists=False):
    formatted_data = {
        "student_id": student_id,
    }

    # map received to database
    attributes = [
        {"received": "accept_studentTot", "database": "studentTot"},
        # Ids
        {"received": "semester_id", "database": "studentEnrollSemester_id"},
        {"received": "stage_id", "database": "studentEnrollStage_id"},
        {"received": "accept_year_id", "database": "studentEnrollYear_id"},
        {"received": "fac_id", "database": "studentFaculty_id"},
        {"received": "univ_id", "database": "studentUniveristy_id"},
        {"received": "registrationType", "database": "studentRegistrationType_id"},
    ]

    if student_exists:
        formatted_data["updatedAt"] = timezone.now()
        formatted_data["updatedBy"] = 0
    else:
        attributes.append({"received": "accept_createdAt", "database": "createdAt"})
        formatted_data["createdBy"] = 0

    for attribute in attributes:
        received = acceptance_data.get(attribute.get("received"))
        if received:
            formatted_data[attribute.get("database")] = received

    return formatted_data


def create_student_records(
    student_basic_data,
    education_data,
    acceptance_data,
    target_student,
    tansiqid,
):
    try:
        with transaction.atomic():
            if target_student:
                Students.objects.filter(id=target_student.get("id")).delete()
                StudentsTransactions.objects.filter(
                    uniqueId=target_student.get("uniqueId"),
                    transactionType_id=TransactionsTypeEnum.ADDED_FROM_TANSIQ.value,
                ).delete()

            # Map student => students
            formatted_student = reformat_student_data(student_basic_data)
            student = Students(**formatted_student)
            student.save()

            # Map studentEdu => studentsecondaryedu
            StudentsSecondaryEdu(
                **reformat_education_data(education_data, student.pk)
            ).save()

            # Map studentAcceptance => studentacceptedapplication
            StudentsAcceptedApplication(
                **reformat_acceptance_data(acceptance_data, student.pk)
            ).save()

            # Map studentAcceptance => studentuniversityedu
            formatted_univ_edu = reformat_university_data(acceptance_data, student.pk)
            StudentsUniversityEdu(**formatted_univ_edu).save()

            create_receive_transaction(
                student.uniqueId,
                None,
                {
                    "tansiqid": tansiqid,
                    "studentStatus_id": formatted_student.get("studentStatus_id"),
                    **formatted_univ_edu,
                },
            )

            return {
                "message": generate_accepted_message(tansiqid, 10, "STUDENT_ACCEPTED")
            }
    except DatabaseError as ex:
        return {
            "message": generate_rejected_message(
                tansiqid, 60, "UNEXPECTED_ERROR", " {0}".format(ex)
            )
        }


def update_university_education(action, target_student, acceptance_data, tansiqid):
    # Map studentAcceptance => studentuniversityedu and update
    formatted_univ_edu = reformat_university_data(
        acceptance_data, target_student.get("id"), True
    )

    formatted_univ_edu[
        "studentRegistrationType_id"
    ] = RegistrationTypeEnum.PRIMARY.value

    if action == "shift":
        formatted_univ_edu["pathShiftDate"] = formate_date(
            acceptance_data.get("accept_createdAt")
        )

    formatted_student = {
        "updatedAt": timezone.now(),
        "updatedBy": 0,
        "studentStatus_id": StudentStatus.INITIALLY_ACCEPTED.value,
        "tansiqid": tansiqid,
    }

    university_education_query = StudentsUniversityEdu.objects.filter(
        student_id=target_student.get("id")
    ).values(
        "studentTot",
        "studentFaculty_id",
        "studentUniveristy_id",
        "studentEnrollYear_id",
        "studentEnrollSemester_id",
        "studentEnrollStage_id",
        "studentRegistrationType_id",
        "pathShiftDate",
    )

    student_query = Students.objects.filter(id=target_student.get("id"))
    original_student_status = target_student.get("studentStatus_id")

    try:
        with transaction.atomic():
            original_univ_edu_data = university_education_query.first()

            university_education_query.update(**formatted_univ_edu)

            student_query.update(**formatted_student)

            if action == "shift":
                create_path_shift_transaction(
                    target_student.get("uniqueId"),
                    {
                        **original_univ_edu_data,
                        "studentStatus_id": original_student_status,
                    },
                    {
                        **formatted_univ_edu,
                        "studentStatus_id": StudentStatus.INITIALLY_ACCEPTED.value,
                    },
                )
                return generate_accepted_message(
                    tansiqid, 14, "STUDENT_PATH_SHIFT_APPLIED"
                )

            else:  # action == "enroll"
                create_receive_transaction(
                    target_student.get("uniqueId"),
                    {
                        "tansiqid": tansiqid,
                        "studentStatus_id": original_student_status,
                        **original_univ_edu_data,
                    },
                )
                return generate_accepted_message(tansiqid, 10, "STUDENT_ACCEPTED")

    except DatabaseError as ex:
        return generate_rejected_message(
            tansiqid, 60, "UNEXPECTED_ERROR", " {0}".format(ex)
        )


def current_year_semester():
    semester_query = Semesters.objects.filter(current=1).values("code")[:1]
    year_query = Years.objects.filter(current=1).values("code")

    values = year_query.annotate(
        current_year_code=F("code"),
        current_semester_code=Subquery(semester_query),
    ).first()

    return (values.get("current_year_code"), values.get("current_semester_code"))


def enroll_year_semester(student_id):
    values = (
        StudentsUniversityEdu.objects.filter(student_id=student_id)
        .values("studentEnrollYear__code", "studentEnrollSemester__code")
        .first()
    )

    return (
        values.get("studentEnrollYear__code"),
        values.get("studentEnrollSemester__code"),
    )


def formate_date(full_date: str, apply_min_10_years=False):
    """
    Convert full_date from `YYYY-MM-DD 00:00:00.00` to `YYYY-MM-DD`
    Args:
        date (str): full_date must be in form of `YYYY-MM-DD 00:00:00.00`
    Returns:
        dict: formatted date if full_date if valid or None if invalid
    """
    result = re.search(ISODatePattern, full_date)
    formatted_date = result.group(0)

    if apply_min_10_years:
        year = formatted_date[:4]
        min = date.today().year - 10

        if int(year) > min:
            return None

    return formatted_date


def exists_in_current_ids(tansiqid):
    cache_key = "ACCEPTED_STUDENTS_CURRENT_IDS"
    current_students_ids: list = cache.get(cache_key, [])

    if tansiqid in current_students_ids:
        return True

    current_students_ids.append(tansiqid)
    cache.set(cache_key, list(current_students_ids), 3600)
    return False


def remove_from_current_ids(tansiq_ids: list):
    cache_key = "ACCEPTED_STUDENTS_CURRENT_IDS"
    current_students_ids: list = cache.get(cache_key, [])

    for tansiqid in tansiq_ids:
        if tansiqid in current_students_ids:
            current_students_ids.remove(tansiqid)

    cache.set(cache_key, current_students_ids, 3600)


def remove_repeated_records():
    """
    Delete repeated students records from database
    - select repeated students by tansiq id
    - delete repeated records from
        - students (by tansiqid)
        - studentstransactions (by uniqueId)
    """
    deleted_records = []

    while True:
        repeated_students_query = """
            SELECT
                id, tansiqid, uniqueId, studentStatus_id
            FROM
                students
            WHERE
                studentStatus_id = 1
            GROUP BY
                tansiqid
            HAVING
                count(tansiqid) > 1
            """

        repeated_records = run_sql_command(repeated_students_query, [], 2)

        if not repeated_records:
            break

        ids = []
        unique_ids = []
        for record in repeated_records:
            deleted_records.append(
                {
                    "id": record.get("id"),
                    "tansiqid": record.get("tansiqid"),
                    "uniqueId": record.get("uniqueId"),
                }
            )
            ids.append(record.get("id"))
            unique_ids.append(record.get("uniqueId"))

        Students.objects.filter(id__in=ids).delete()
        StudentsTransactions.objects.filter(uniqueId__in=unique_ids).delete()

    return {
        "deleted_count": len(deleted_records),
        "deleted_ids": deleted_records,
    }
