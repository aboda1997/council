import json
import re
from base64 import b64encode
from datetime import datetime
from os import urandom

from django.db import DatabaseError, transaction

from core.models.db import (
    Students,
    StudentsSecondaryEdu,
    StudentsTransactions,
    StudentsUniversityEdu,
    Faculties,
)
from core.services.oldCouncilDataMigration.constants import (
    FLAGS,
    MESSAGES,
    MODES,
    SECONDARY_EDUCATION_MAPPING,
    STAGE_MAPPING,
    STAGE_NOTES,
    STUDENT_ATTRIBUTES,
    UNIVERSITY_EDUCATION_MAPPING,
)
from core.services.oldCouncilDataMigration.validation import ValidationRules
from core.utils.enums import (
    DisallowedCharactersPattern,
    DisallowedExtraSpacesPattern,
    ISODatePattern,
    NIDPattern,
    NoSymbolsPattern,
    PhonePattern,
    StudentStatus,
)
from core.utils.validators import Validation


def add_students(
    faculty, students, council_ids_map, mode, error_flags, output_flags
):  # noqa: C901
    """
    return a report with actual` count of students in the faculty, count of
    successfully stored students, and count of failed with reason of failure
    """
    passed_reports = []
    exist_students = []
    failed_reports = []
    replaced_reports = []
    passed_count = 0
    exist_count = 0
    replaced_count = 0
    failed_count = 0
    student_record = None

    for student_data in students:
        old_council_id = None
        store_student = True
        student_exists = False
        replace_exist_student = False
        errors = []

        if isinstance(student_data, dict) and "student" in student_data:
            old_council_id = student_data.get("student").get("id")

        # check if student_data is a dict contains the required three dictionaries
        result = check_data_format(student_data)
        if not result.get("success"):
            store_student = False
            errors.append(result.get("message"))

        # check if student has an id
        if not old_council_id:
            store_student = False
            if "id" in error_flags:
                errors.append(MESSAGES.get("MISSING_STUDENT_ID"))

        basic_data = student_data.get("student")
        secondary_education = student_data.get("secondaryEdu")
        university_education = student_data.get("studentUniversityEdu")

        # check if student already exists
        result = check_student_existence(
            basic_data,
            university_education.get("AcceptDate"),
            mode,
            errors,
            error_flags,
        )
        student_exists = result.get("student_exists")
        replace_exist_student = result.get("replace_student")
        student_record = result.get("student")

        if student_exists and not replace_exist_student:
            exist_count += 1
            exist_students.append(
                generate_student_report(
                    old_council_id, student_data, store_student, output_flags, errors
                )
            )
            continue

        # append studentUniveristy_id and studentTot to university_education
        university_education["studentUniveristy_id"] = faculty.get("univ_id")
        university_education["studentTot"] = secondary_education.get(
            "studentTotalDegree"
        )

        # generate a unique id
        basic_data["uniqueId"] = generate_student_unique_id()

        if university_education.get("RegistrationTypeID") == "-1":
            university_education["transferDate"] = re.search(
                ISODatePattern, university_education.get("AcceptDate", "")
            ).group(0)

        check_national_id(basic_data, errors, error_flags)

        check_student_name(basic_data, errors, error_flags)

        check_phone_number(basic_data, errors, error_flags)

        check_notes(basic_data, university_education, errors, error_flags)

        # check total degree and equivalent total degree
        check_student_degree(secondary_education, errors, error_flags)

        # check graduation GPA (Special case)
        graduation_gpa: str = university_education.get("studentGraduationGPA")
        if "%" in graduation_gpa:
            graduation_gpa = graduation_gpa.replace("%", "")
            university_education["studentGraduationPercentage"] = graduation_gpa
            university_education["studentGraduationGPA"] = None
            errors.extend(MESSAGES.get("PERCENT_FOUND_IN_GPA"))

        # validate all fields
        validation_result = Validation.run_all_validators(
            [
                *ValidationRules.student(basic_data),
                *ValidationRules.secondary_education(secondary_education),
                *ValidationRules.university_education(university_education),
            ]
        )
        if not validation_result.get("success"):
            for error in validation_result.get("errors"):
                if error.get("flag") in error_flags:
                    errors.append(
                        "{message}, found `{value}`".format(
                            message=MESSAGES.get(error.get("message")),
                            value=error.get("value"),
                        )
                    )

        # set the fixed ids before mapping
        fix_level_id(university_education)

        # check all old council ids if exist in the new council tables
        result = ValidationRules.validate_old_council_ids(student_data, council_ids_map)
        if not result.get("success"):
            store_student = False
            errors.extend(result.get("messages"))

        map_stage_id(basic_data, university_education)

        if mode == MODES.get("REPORT"):
            student_data = reformat_student_data(
                basic_data,
                secondary_education,
                university_education,
                old_council_id,
            )
        elif store_student and (not student_exists or replace_exist_student):
            result = create_student_records(
                basic_data,
                secondary_education,
                university_education,
                replace_exist_student,
                student_record,
            )
            if not result.get("success"):
                store_student = False
                errors.append(result.get("message"))

        # count the student
        if replace_exist_student:
            replaced_count += 1
        elif store_student:
            passed_count += 1
        else:
            failed_count += 1

        # append errors to reports
        if errors or mode == MODES.get("REPORT"):
            report = generate_student_report(
                old_council_id, student_data, store_student, output_flags, errors
            )
            if replace_exist_student:
                replaced_reports.append(report)
            elif store_student:
                passed_reports.append(report)
            else:
                failed_reports.append(report)

    return generate_final_report(
        faculty,
        students,
        exist_students,
        replaced_reports,
        passed_reports,
        failed_reports,
        exist_count,
        passed_count,
        failed_count,
        replaced_count,
    )


def update_invalid_students(students, council_ids_map, error_flags):  # noqa: C901
    """
    update invalid students with withdrawn records
    """
    replaced_reports = []
    failed_reports = []

    for student_data in students:
        student_record = None
        old_council_id = None
        messages = []

        if isinstance(student_data, dict) and "student" in student_data:
            old_council_id = student_data.get("student").get("id")

        # check if student_data is a dict contains the required three dictionaries
        result = check_data_format(student_data)
        if not result.get("success"):
            messages.append(result.get("message"))
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )
            continue

        # check if student has an id
        if not old_council_id:
            if "id" in error_flags:
                messages.append(MESSAGES.get("MISSING_STUDENT_ID"))
                failed_reports.append(
                    generate_student_report(
                        old_council_id, student_data, False, [], messages
                    )
                )
            continue

        basic_data = student_data.get("student")
        secondary_education = student_data.get("secondaryEdu")
        university_education = student_data.get("studentUniversityEdu")

        old_faculty_id = university_education.get("studentFaculty_id")
        faculty = (
            Faculties.objects.filter(oldcouncilid=old_faculty_id)
            .values("id", "oldcouncilid", "univ_id", "name")
            .first()
        )

        if not faculty:
            messages.append(
                MESSAGES.get("FACULTY_NOT_FOUND").format(faculty_id=old_faculty_id)
            )
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )
            continue

        # check if student already exists
        student_record = (
            Students.objects.filter(oldcouncilid=old_council_id)
            .values("id", "createdAt", "uniqueId", "studentStatus_id")
            .first()
        )

        if not student_record:
            messages.append(MESSAGES.get("STUDENT_NOT_FOUND"))
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )
            continue
        elif student_record.get("studentStatus_id") != StudentStatus.WITHDRAWN.value:
            messages.append(MESSAGES.get("CAN_NOT_UPDATE_STUDENT"))
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )
            continue

        # append studentUniveristy_id and studentTot to university_education
        university_education["studentUniveristy_id"] = faculty.get("univ_id")
        university_education["studentTot"] = secondary_education.get(
            "studentTotalDegree"
        )

        # generate a unique id
        basic_data["uniqueId"] = student_record.get("uniqueId")

        if university_education.get("RegistrationTypeID") == "-1":
            university_education["transferDate"] = re.search(
                ISODatePattern, university_education.get("AcceptDate", "")
            ).group(0)

        check_national_id(basic_data, messages, error_flags)
        check_student_name(basic_data, messages, error_flags)
        check_phone_number(basic_data, messages, error_flags)
        check_notes(basic_data, university_education, messages, error_flags)
        check_student_degree(secondary_education, messages, error_flags)

        # check graduation GPA (Special case)
        graduation_gpa: str = university_education.get("studentGraduationGPA")
        if "%" in graduation_gpa:
            graduation_gpa = graduation_gpa.replace("%", "")
            university_education["studentGraduationPercentage"] = graduation_gpa
            university_education["studentGraduationGPA"] = None
            messages.extend(MESSAGES.get("PERCENT_FOUND_IN_GPA"))

        # validate all fields
        validation_result = Validation.run_all_validators(
            [
                *ValidationRules.student(basic_data),
                *ValidationRules.secondary_education(secondary_education),
                *ValidationRules.university_education(university_education),
            ]
        )
        if not validation_result.get("success"):
            for error in validation_result.get("errors"):
                if error.get("flag") in error_flags:
                    messages.append(
                        "{message}, found `{value}`".format(
                            message=MESSAGES.get(error.get("message")),
                            value=error.get("value"),
                        )
                    )

        # set the fixed ids before mapping
        fix_level_id(university_education)

        # check all old council ids if exist in the new council tables
        result = ValidationRules.validate_old_council_ids(student_data, council_ids_map)
        if not result.get("success"):
            messages.extend(result.get("messages"))
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )
            continue

        map_stage_id(basic_data, university_education)

        student_current_id = student_record.get("id")

        try:
            with transaction.atomic():
                Students.objects.get(id=student_current_id).delete()
                StudentsTransactions.objects.filter(
                    uniqueId=student_record.get("uniqueId")
                ).delete()

                student_new_id = save_student_records(
                    basic_data, secondary_education, university_education
                )

                create_transfer_transaction(basic_data, university_education)

                messages.append(
                    f"Student with id:`{student_current_id}` has been replaced with new record with id:`{student_new_id}`"
                )
                replaced_reports.append(
                    generate_student_report(
                        old_council_id, student_data, True, [], messages
                    )
                )
        except DatabaseError as db_error:
            messages.append(MESSAGES.get("UNEXPECTED_DB_ERROR") + ", " + str(db_error))
            failed_reports.append(
                generate_student_report(
                    old_council_id, student_data, False, [], messages
                )
            )

    return {
        "results": {
            "replaced_count": len(replaced_reports),
            "failed_count": len(failed_reports),
        },
        "replaced_reports": replaced_reports,
        "failed_reports": failed_reports,
    }


def check_data_format(student_data):
    if not isinstance(student_data, dict) or (
        "student" not in student_data
        or "secondaryEdu" not in student_data
        or "studentUniversityEdu" not in student_data
    ):
        return {"success": False, "message": MESSAGES.get("INVALID_STUDENT_FORMAT")}
    return {"success": True}


def check_student_existence(basic_data, accept_date, mode, errors, error_flags):
    student_exists = False
    target_student: Students = None
    replace_student = False
    old_council_id = basic_data.get("id")
    if old_council_id and mode == MODES.get("STORE"):
        target_student = (
            Students.objects.filter(oldcouncilid=old_council_id)
            .values("id", "createdAt")
            .first()
        )
        if target_student:
            student_exists = True
            current_created_at = datetime.fromisoformat(
                str(target_student.get("createdAt"))[:-6]
            )
            replace_student = datetime.fromisoformat(accept_date) > current_created_at
            if replace_student:
                if FLAGS.get("REPEATED_STUDENT") in error_flags:
                    errors.append(MESSAGES.get("STUDENT_ALREADY_EXISTS_REPLACE"))
            else:
                if FLAGS.get("REPEATED_STUDENT") in error_flags:
                    errors.append(MESSAGES.get("STUDENT_ALREADY_EXISTS"))

    return {
        "student_exists": student_exists,
        "replace_student": replace_student,
        "student": target_student,
    }


def generate_student_unique_id(creation_date=datetime.now()):
    if isinstance(creation_date, str):
        creation_date = datetime.fromisoformat(creation_date)
    unix_timestamp = str(int(creation_date.timestamp()))[4:]
    uid = re.sub(r"[/+]", "0", b64encode(urandom(9)).decode('UTF-8')).upper()
    return unix_timestamp + "-" + uid[:6] + "-" + uid[7:]


def check_national_id(basic_data, errors, error_flags):
    national_id = basic_data.get("studentNID") or None
    if national_id:
        if len(national_id) != 14 or not re.search(NIDPattern, national_id):
            basic_data["studentNID"] = None
            if "studentNID" in error_flags:
                errors.append(
                    MESSAGES.get("INVALID_NATIONAL_ID").format(national_id=national_id)
                )
        else:
            century = national_id[0:1]
            birth_year = (
                "19" + national_id[1:3] if century == "2" else "20" + national_id[1:3]
            )

            # studentBirthDate, YYYY-MM-DD
            student_birthdate = (
                birth_year + "-" + national_id[3:5] + "-" + national_id[5:7]
            )
            # studentGender_id, "0"->male | "1"->female (before mapping ids)
            student_gender_id = "0" if int(national_id[12:13]) % 2 != 0 else "1"

            basic_data["studentBirthDate"] = student_birthdate
            basic_data["studentGender_id"] = student_gender_id


def check_student_name(basic_data, errors, error_flags):
    student_name: str = basic_data.get("studentNameAr")
    if student_name:
        # special case: name ends with (م)
        student_name = student_name.replace("(م)", "")
        student_name = re.sub(DisallowedCharactersPattern, "", student_name)
        student_name = re.sub(DisallowedExtraSpacesPattern, "", student_name)

        if not re.search(NoSymbolsPattern, student_name):
            if "studentNameAr" in error_flags:
                value = basic_data.get("studentNameAr")
                errors.append(
                    MESSAGES.get("INVALID_STUDENT_NAME_LETTERS")
                    + f", found `{value}` and replaced with `{student_name}`"
                )

        basic_data["studentNameAr"] = student_name.strip()


def check_phone_number(basic_data, errors, error_flags):
    phone_number = basic_data.get("studentPhone")
    if phone_number and not re.search(PhonePattern, phone_number):
        basic_data["studentPhone"] = None
        if "studentPhone" in error_flags:
            errors.append(
                MESSAGES.get(
                    "INVALID_PHONE_FORMAT"
                    + f", found `{phone_number}` and set to `null`"
                )
            )


def check_notes(basic_data, university_education, errors, error_flags):
    # remove "DB Entry " from notes if found
    notes: str = basic_data.get("notes").strip()

    if "DB Entry" in notes:
        notes = notes.replace("DB Entry", "").strip()
        if "notes" in error_flags:
            errors.append(MESSAGES.get("NOTES_UPDATE"))

    # for transferred students append the previous university data to the notes
    previous_univ_notes: str = university_education.get("OriginalUniName", "").strip()
    if previous_univ_notes and previous_univ_notes not in notes:
        notes += "\n" + previous_univ_notes

    basic_data["notes"] = notes.strip()


def check_student_degree(secondary_education, errors, error_flags):
    if not secondary_education.get("studentSecondaryCert_id"):
        if "studentSecondaryCert_id" in error_flags:
            errors.append(MESSAGES.get("MISSING_CERT_ID"))
    else:
        total_degree = secondary_education.get("studentTotalDegree")
        equiv_total_degree = secondary_education.get("studentEquivTotalDegree")

        if total_degree == "0":
            secondary_education["studentTotalDegree"] = None
        if equiv_total_degree == "0":
            secondary_education["studentEquivTotalDegree"] = None

        # student total degree is required if (GS) student
        if str(secondary_education.get("studentSecondaryCert_id")) == "1":
            # "1" for general secondary students (GS) in the old council
            if not total_degree and "studentTotalDegree" in error_flags:
                errors.append(MESSAGES.get("MISSING_TOTAL_DEGREE"))
        else:
            # student equivalent is required if non (GS) student
            if not equiv_total_degree and "studentEquivTotalDegree" in error_flags:
                errors.append(MESSAGES.get("MISSING_EQUIV_DEGREE"))


def fix_level_id(university_education):
    level: str = university_education.get("ConvertLevel")

    if level == "0" or level == "":
        university_education["ConvertLevel"] = None
    elif level and level.isdigit():
        university_education["ConvertLevel"] = int(level)


def map_stage_id(basic_data, university_education):
    stage_id = university_education.get("studentEnrollStage_id")

    for item in STAGE_MAPPING:
        if int(stage_id) in item.get("stage_id"):
            university_education["studentEnrollSemester_id"] = item.get("semester")
            university_education["studentEnrollStage_id"] = item.get("stage")

            stage_name = STAGE_NOTES.get(stage_id)
            if stage_name:
                migration_notes_str = basic_data.get("migration_notes", "{}")
                try:
                    migration_notes = json.loads(migration_notes_str)
                except json.JSONDecodeError:
                    migration_notes = {}

                migration_notes["stage_notes"] = {
                    "old_council_stage_id": stage_id,
                    "old_council_stage_name": stage_name,
                }

                basic_data["migration_notes"] = json.dumps(
                    migration_notes, ensure_ascii=False
                )

            break


def reformat_student_data(
    basic_data, secondary_education, university_education, old_council_id
):
    # Map student => students
    basic_data = reformat_basic_data(basic_data, university_education)

    # Map secondaryEdu => studentsecondaryedu
    secondary_education = reformat_secondary_education(
        secondary_education, university_education, old_council_id, None
    )

    # Map studentUniversityEdu => studentuniversityedu
    university_education = reformat_university_education(university_education, None)

    return {
        "basic_data": basic_data,
        "secondary_education": secondary_education,
        "university_education": university_education,
    }


def create_student_records(
    basic_data,
    secondary_education,
    university_education,
    replace_current_records,
    current_student_record,
):
    try:
        with transaction.atomic():
            if replace_current_records:
                Students.objects.get(id=current_student_record.get("id")).delete()

            save_student_records(basic_data, secondary_education, university_education)

            create_transfer_transaction(basic_data, university_education)

            return {"success": True}
    except DatabaseError as db_error:
        return {
            "success": False,
            "message": {
                "message": MESSAGES.get("UNEXPECTED_DB_ERROR"),
                "database_error_msg": str(db_error),
            },
        }


def save_student_records(basic_data, secondary_education, university_education):
    old_council_id = basic_data.get("id")

    # Map student => students
    student = Students(**reformat_basic_data(basic_data, university_education))
    student.save()

    # Map secondaryEdu => studentsecondaryedu
    StudentsSecondaryEdu(
        **reformat_secondary_education(
            secondary_education,
            university_education,
            old_council_id,
            student.pk,
        )
    ).save()

    # Map studentUniversityEdu => studentuniversityedu
    StudentsUniversityEdu(
        **reformat_university_education(university_education, student.pk)
    ).save()

    return student.pk


def create_transfer_transaction(basic_data, university_education):
    # After mapping ids
    if university_education.get("transferDate"):
        transfer_date = university_education.get("transferDate")
        user_id = 0  # 0 -> system

        # Accept Date = Modified Date => the record added by `user_id` and never updated
        if university_education.get("ModifiedDate") == transfer_date:
            user_id = university_education.get("UserID")

        originalData = {}
        if university_education.get("OriginalFacultyID"):
            originalData = {
                "studentFaculty_id": university_education.get("OriginalFacultyID"),
                "studentUniveristy_id": university_education.get("OriginalUniID"),
            }

        updatedData = {
            "transferDate": transfer_date,
            "studentFaculty_id": university_education.get("studentFaculty_id"),
            "studentUniveristy_id": university_education.get("studentUniveristy_id"),
            "studentEnrollYear_id": university_education.get("studentEnrollYear_id"),
            "studentEnrollSemester_id": university_education.get(
                "studentEnrollSemester_id"
            ),
            "studentEnrollStage_id": university_education.get("studentEnrollStage_id"),
            "studentLevel_id": university_education.get("ConvertLevel"),
            "totalEquivalentHours": university_education.get("TotalEquivalentHours"),
        }

        StudentsTransactions(
            createdBy=user_id,
            transactionType_id=26,
            uniqueId=basic_data.get("uniqueId"),
            originalData=json.dumps(originalData, ensure_ascii=False),
            updatedData=json.dumps(updatedData, ensure_ascii=False),
        ).save()


def reformat_basic_data(basic_data, university_education):
    formatted_data = {
        "oldcouncilid": basic_data.get("id"),
        "studentName": basic_data.get("studentNameAr") + "|",
        "studentStatus_id": university_education.get("AcceptanceStatus"),
    }

    append_data(formatted_data, university_education)

    for attribute in STUDENT_ATTRIBUTES:
        received = basic_data.get(attribute)
        if isinstance(received, str):
            received = received.strip()
        if received:
            formatted_data[attribute] = received

    return formatted_data


def reformat_secondary_education(
    secondary_education, university_education, old_council_id, student_id
):
    formatted_data = {
        "student_id": student_id,
    }

    append_data(formatted_data, university_education)

    # get seat number for (GS) students
    if str(secondary_education.get("studentSecondaryCert_id")) == "1":
        if len(old_council_id) > 4:
            formatted_data["studentSeatNumber"] = old_council_id[:-4]

    for attribute in SECONDARY_EDUCATION_MAPPING:
        received = secondary_education.get(attribute[0])
        if isinstance(received, str):
            received = received.strip()
        if received:
            formatted_data[attribute[1]] = received

    return formatted_data


def reformat_university_education(university_education, student_id):
    formatted_data = {
        "student_id": student_id,
    }

    append_data(formatted_data, university_education)

    for attribute in UNIVERSITY_EDUCATION_MAPPING:
        received = university_education.get(attribute[0])
        if isinstance(received, str):
            received = received.strip()
        if received:
            formatted_data[attribute[1]] = received

    return formatted_data


def append_data(formatted_data, university_education):
    created_at = university_education.get("AcceptDate")
    updated_by = university_education.get("UserID")
    updated_at = university_education.get("ModifiedDate")
    if created_at:
        formatted_data["createdAt"] = created_at
    if updated_by:
        formatted_data["updatedBy"] = updated_by
    if updated_at:
        formatted_data["updatedAt"] = updated_at


def generate_student_report(
    old_council_id, student_data, passed, output_flags, errors=[]
):
    report = {
        "id": old_council_id,
        "status": "passed" if passed else "failed",
        "messages": errors,
    }
    if FLAGS.get("FULL_STUDENT_DATA") in output_flags:
        report["student"] = student_data
    return report


def generate_final_report(
    faculty,
    students,
    exist_students,
    replaced_reports,
    passed_reports,
    failed_reports,
    exist_count,
    passed_count,
    failed_count,
    replaced_count,
):
    return {
        "faculty": {
            **faculty,
            "students_count": len(students),
        },
        "results": {
            "exist_students_count": exist_count,
            "replaced_count": replaced_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
        },
        "reports_count": {
            "passed_reports_count": len(passed_reports),
            # "missing_ids_repeat_count": missing_ids,
        },
        "exist_students": exist_students,
        "replaced_reports": replaced_reports,
        "passed_reports": passed_reports,
        "failed_reports": failed_reports,
    }
