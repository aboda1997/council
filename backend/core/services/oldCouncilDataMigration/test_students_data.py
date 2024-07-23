import json
import re
from datetime import datetime

from core.models.db import (
    Students,
    StudentsSecondaryEdu,
    StudentsUniversityEdu,
    Years,
)
from core.services.oldCouncilDataMigration.constants import MESSAGES
from core.services.oldCouncilDataMigration.council_mapping_ids import (
    MAPPING_IDS,
    STAGE_MAPPING,
)
from core.utils.enums import (
    DisallowedCharactersPattern,
    DisallowedExtraSpacesPattern,
    ISODatePattern,
    NIDPattern,
    PhonePattern,
)


def test_students(faculty, students):
    reports = []
    passed_count = 0
    failed_count = 0
    replaced_count = 0

    for student_data in students:
        old_council_id = None
        errors = []
        data_check_success = True

        if isinstance(student_data, dict) and "student" in student_data:
            old_council_id = student_data.get("student").get("id")

        # check if student_data is a dict contains the required three dictionaries
        result = check_data_format(student_data)
        if not result.get("success"):
            errors.append(result.get("message"))
            reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            failed_count = failed_count + 1
            continue

        # check if student has an id
        if not old_council_id:
            errors.append(MESSAGES.get("MISSING_STUDENT_ID"))
            reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            failed_count = failed_count + 1
            continue

        # check if student existence
        student: Students = check_student_existence(old_council_id)
        if not student:
            errors.append(MESSAGES.get("STUDENT_NOT_FOUND"))
            reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            failed_count = failed_count + 1
            continue

        accept_date = student_data.get("studentUniversityEdu").get("AcceptDate")
        created_date = str(student.createdAt)[:-6]
        if accept_date != created_date:
            errors.append(MESSAGES.get("STUDENT_REPLACED"))
            reports.append(
                generate_report(old_council_id, student_data, "replaced", errors)
            )
            replaced_count += 1
            continue

        secondary_education, university_education = get_student_education(student.pk)
        if not secondary_education or not university_education:
            errors.append(MESSAGES.get("STUDENT_RECORDS_NOT_FOUND"))
            reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            failed_count = failed_count + 1
            continue

        student_all_data = {
            **student_data.get("student"),
            **student_data.get("secondaryEdu"),
            **student_data.get("studentUniversityEdu"),
        }

        # check student
        certificate_year: Years = secondary_education.studentCertificateYear
        certificate_year_code = certificate_year.code if certificate_year else None
        messages = check_basic_data(student, student_all_data, certificate_year_code)
        if messages:
            errors.extend(messages)
            data_check_success = False

        # check secondary education
        messages = check_secondary_education(secondary_education, student_all_data)
        if messages:
            errors.extend(messages)
            data_check_success = False

        # check university education
        messages = check_university_education(
            university_education, student_all_data, faculty
        )
        if messages:
            errors.extend(messages)
            data_check_success = False

        if data_check_success:  # all data are correct
            passed_count = passed_count + 1
        else:
            failed_count = failed_count + 1
            reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )

    return {
        "faculty": {
            **faculty,
            "students_count": len(students),
        },
        "results": {
            "replaced_count": replaced_count,
            "passed_count": passed_count,
            "failed_count": failed_count,
        },
        "reports_count": len(reports),
        "reports": reports,
    }


def test_invalid_students(students):
    replaced_reports = []
    failed_reports = []

    for student_data in students:
        old_council_id = None
        errors = []
        data_check_success = True

        if isinstance(student_data, dict) and "student" in student_data:
            old_council_id = student_data.get("student").get("id")

        # check if student_data is a dict contains the required three dictionaries
        result = check_data_format(student_data)
        if not result.get("success"):
            errors.append(result.get("message"))
            failed_reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            continue

        # check if student has an id
        if not old_council_id:
            errors.append(MESSAGES.get("MISSING_STUDENT_ID"))
            failed_reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            continue

        # check if student existence
        student: Students = check_student_existence(old_council_id)
        if not student:
            errors.append(MESSAGES.get("STUDENT_NOT_FOUND"))
            failed_reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            continue

        secondary_education, university_education = get_student_education(student.pk)
        if not secondary_education or not university_education:
            errors.append(MESSAGES.get("STUDENT_RECORDS_NOT_FOUND"))
            failed_reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
            )
            continue

        student_all_data = {
            **student_data.get("student"),
            **student_data.get("secondaryEdu"),
            **student_data.get("studentUniversityEdu"),
        }

        # check student
        certificate_year: Years = secondary_education.studentCertificateYear
        certificate_year_code = certificate_year.code if certificate_year else None
        messages = check_basic_data(student, student_all_data, certificate_year_code)
        if messages:
            errors.extend(messages)
            data_check_success = False

        # check secondary education
        messages = check_secondary_education(secondary_education, student_all_data)
        if messages:
            errors.extend(messages)
            data_check_success = False

        # check university education
        messages = check_university_education(
            university_education,
            student_all_data,
            {
                "id": university_education.studentFaculty.pk,
                "univ_id": university_education.studentUniveristy.pk,
            },
        )
        if messages:
            errors.extend(messages)
            data_check_success = False

        if data_check_success:  # all data are correct
            replaced_reports.append(
                generate_report(old_council_id, student_data, "replaced", errors)
            )
        else:
            failed_reports.append(
                generate_report(old_council_id, student_data, "failed", errors)
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


def check_student_existence(old_council_id):
    target_student = Students.objects.filter(oldcouncilid=old_council_id)
    return target_student.first()


def get_student_education(student_id):
    return (
        StudentsSecondaryEdu.objects.filter(student_id=student_id).first(),
        StudentsUniversityEdu.objects.filter(student_id=student_id).first(),
    )


def check_basic_data(student: Students, student_data, cert_year_code):
    mapping_values = []

    # ["studentNID"] [optional]
    #   - empty or invalid -> null
    #   - valid -> the same + check gender and birthdate
    national_id = student_data.get("studentNID") or None
    if national_id:
        if len(national_id) != 14 or not re.search(NIDPattern, national_id):
            national_id = None
        else:
            data = extract_data_from_national_id(national_id)
            student_data["studentGender_id"] = data.get("gender_id")

            # studentBirthDate [calculated from the national id]
            mapping_values.append(
                (
                    "studentBirthDate",
                    data.get("birthdate"),
                    str(student.studentBirthDate),
                )
            )

    mapping_values.append(("studentNID", national_id, student.studentNID))

    # ["studentNameAr"] [required]
    #   - remove disallowed characters, trim and remove extra spaces
    #   - append `|` to the name
    #   - special case: name ends with (م)
    student_name = student_data.get("studentNameAr")
    student_name = student_name.replace("(م)", "")
    student_name = re.sub(DisallowedCharactersPattern, "", student_name)
    student_name = re.sub(DisallowedExtraSpacesPattern, "", student_name)
    student_name = student_name.strip() + "|"

    mapping_values.append(("studentNameAr", student_name, student.studentName))

    # ["studentPhone"] [optional]
    #   - validate (PhonePattern)
    #       - invalid -> null
    #       - valid -> the same
    phone_number = student_data.get("studentPhone")
    phone_number = phone_number.strip()
    if phone_number and not re.search(PhonePattern, phone_number):
        phone_number = None
    mapping_values.append(("studentPhone", phone_number, student.studentPhone))

    # ["studentAddress"] [optional]
    #   - trim spaces
    address: str = student_data.get("studentAddress")
    address = address.strip()
    mapping_values.append(("studentAddress", address, student.studentAddress))

    # ["notes"] [optional]
    #   - Remove "DB Entry", trim and remove extra spaces
    #   - append a message to the note according to "studentEnrollStage_id
    #   - use -> STAGE_MAPPING
    notes: str = student_data.get("notes")
    notes = notes.replace("DB Entry", "").strip()

    previous_univ_notes = student_data.get("OriginalUniName", "").strip()
    if previous_univ_notes and previous_univ_notes not in notes:
        notes += "\n" + previous_univ_notes

    mapping_values.append(("notes", notes.strip(), student.notes))

    # ----- * ----- ids ----- * -----

    # ["studentGender_id"] [required] ["0", "1", "2"]
    #   - use MAPPING_IDS["gender"]
    gender_id = student_data.get("studentGender_id")
    mapped_gender_id = MAPPING_IDS.get("gender").get(gender_id)

    student_gender = student.studentGender
    student_gender_id = student_gender.id if student_gender else None

    mapping_values.append(("studentGender_id", mapped_gender_id, student_gender_id))

    # ["studentNationality_id"] [required]
    #   - use MAPPING_IDS["regions"]
    nationality_id = student_data.get("studentNationality_id")
    mapped_nationality_id = MAPPING_IDS.get("regions").get(nationality_id)

    nationality = student.studentNationality
    nationality_id = nationality.id if nationality else None

    mapping_values.append(
        ("studentNationality_id", mapped_nationality_id, nationality_id)
    )

    # ----- * ----- * ----- * -----

    # updatedAt ["ModifiedDate"] & updatedBy ["UserID"]
    mapping_values.extend(
        check_modification_info(student_data, student.updatedAt, student.updatedBy)
    )

    # studentStatus_id ["AcceptanceStatus"]
    status = student_data.get("AcceptanceStatus")
    mapped_status = MAPPING_IDS.get("status").get(status)

    student_status = student.studentStatus
    student_status_id = student_status.id if student_status else None

    mapping_values.append(("AcceptanceStatus", mapped_status, student_status_id))

    # ----- Compare values -----
    messages = compare_values(student_data, mapping_values, "student")

    # uniqueId
    #   - uniqueId must exist and starts with (certificate year code)
    unique_id: str = student.uniqueId or ""
    if not unique_id or len(unique_id) != 19:
        messages.append(
            create_mismatching_values_message(
                "student",
                "uniqueId",
                None,
                "A UNIQUE ID OF LENGTH OF 19",
                student.uniqueId,
            )
        )

    # oldcouncilid
    #   - student has already selected by oldcouncilid

    # migration_notes
    migration_note_matches = True
    stage_id = student_data.get("studentEnrollStage_id")
    stage_map = STAGE_MAPPING.get(stage_id)
    if stage_map and stage_map.get("note"):
        migration_notes = student.migration_notes
        found_note = None
        expected_note = None

        try:
            migration_notes = json.loads(migration_notes)
            found_note = migration_notes.get("stage_notes")
            expected_note = stage_map.get("note")
            if (
                found_note.get("old_council_stage_id") != stage_id
                or found_note.get("old_council_stage_name") != expected_note
            ):
                migration_note_matches = False
        except (Exception):
            migration_note_matches = False

        if not migration_note_matches:
            found_note = (
                found_note.get("old_council_stage_name") if found_note else None
            )
            messages.append(
                create_mismatching_values_message(
                    "student", "migration_notes", None, expected_note, found_note
                )
            )

    return messages


def check_secondary_education(secondary_education: StudentsSecondaryEdu, student_data):
    mapping_values = []

    # studentSecondaryCert_id ["studentSecondaryCert_id"] [required]
    #   - use MAPPING_IDS["certificates :]
    certificate_id = student_data.get("studentSecondaryCert_id")
    mapped_certificate_id = MAPPING_IDS.get("certificates").get(certificate_id)

    certificate = secondary_education.studentSecondaryCert
    certificate_id = certificate.id if certificate else None

    mapping_values.append(
        ("studentSecondaryCert_id", mapped_certificate_id, certificate_id)
    )

    # studentSeatNumber (extracted from id for GS students)
    if certificate_id and certificate_id == 1:
        old_council_id = student_data.get("id")
        seat_number = old_council_id[:-4] if old_council_id else None

        mapping_values.append(
            ("seat_number", seat_number, secondary_education.studentSeatNumber)
        )

    # studentTot ["studentTotalDegree"]
    total_degree = student_data.get("studentTotalDegree")
    if total_degree == "" or total_degree == "0":
        total_degree = None

    mapping_values.append(
        ("studentTotalDegree", total_degree, secondary_education.studentTot)
    )

    # studentEquivTot ["studentEquivTotalDegree"]
    total_equiv_degree = student_data.get("studentEquivTotalDegree")
    if total_equiv_degree == "" or total_equiv_degree == "0":
        total_equiv_degree = None

    mapping_values.append(
        (
            "studentEquivTotalDegree",
            total_equiv_degree,
            secondary_education.studentEquivTot,
        )
    )

    # studentCertificateYear_id ["certificateYear_id"] [required]
    certificate_year_id = student_data.get("certificateYear_id")
    mapped_certificate_year_id = MAPPING_IDS.get("years").get(certificate_year_id)

    certificate_year = secondary_education.studentCertificateYear
    certificate_year_id = certificate_year.id if certificate_year else None

    mapping_values.append(
        ("certificateYear_id", mapped_certificate_year_id, certificate_year_id)
    )

    # studentStudyGroup_id ["studentDeptCode_id"] [required]
    study_group_id = student_data.get("studentDeptCode_id")
    mapped_study_group_id = MAPPING_IDS.get("studygroups").get(study_group_id)

    study_group = secondary_education.studentStudyGroup
    study_group_id = study_group.id if study_group else None

    mapping_values.append(("studentDeptCode_id", mapped_study_group_id, study_group_id))

    # updatedAt ["ModifiedDate"] & updatedBy ["UserID"]
    mapping_values.extend(
        check_modification_info(
            student_data, secondary_education.updatedAt, secondary_education.updatedBy
        )
    )

    # ----- Compare values -----
    return compare_values(student_data, mapping_values, "secondary education")


def check_university_education(
    university_education: StudentsUniversityEdu, student_data, faculty
):
    mapping_values = []

    old_enroll_stage_id = student_data.get("studentEnrollStage_id")
    mapped_enroll_stage = STAGE_MAPPING.get(old_enroll_stage_id)

    # studentEnrollSemester_id
    expected_value = mapped_enroll_stage.get("semester")

    enroll_semester = university_education.studentEnrollSemester
    actual_value = enroll_semester.id if enroll_semester else None

    mapping_values.append(("studentEnrollSemester_id", expected_value, actual_value))

    # studentEnrollStage_id
    expected_value = mapped_enroll_stage.get("stage")

    enroll_stage = university_education.studentEnrollStage
    actual_value = enroll_stage.id if enroll_stage else None

    mapping_values.append(("studentEnrollStage_id", expected_value, actual_value))

    # ----- * -----

    # studentFaculty_id
    student_faculty = university_education.studentFaculty
    student_faculty_id = student_faculty.id if student_faculty else None

    mapping_values.append(("studentFaculty_id", faculty.get("id"), student_faculty_id))

    # studentUniveristy_id
    student_university = university_education.studentUniveristy
    student_university_id = student_university.id if student_university else None

    mapping_values.append(
        ("studentUniveristy_id", student_university_id, faculty.get("univ_id"))
    )

    # ----- * -----

    # studentEnrollYear_id ["studentEnrollYear_id"]
    mapping_values.append(
        check_ids(
            student_data,
            "studentEnrollYear_id",
            "years",
            university_education.studentEnrollYear,
        )
    )

    # studentActualGraduationMonth_id ["studentGraduationMonth_id"]
    mapping_values.append(
        check_ids(
            student_data,
            "studentGraduationMonth_id",
            "months",
            university_education.studentActualGraduationMonth,
        )
    )

    # studentActualGraduationYear_id ["studentGraduationYear_id"]
    mapping_values.append(
        check_ids(
            student_data,
            "studentGraduationYear_id",
            "years",
            university_education.studentActualGraduationYear,
        )
    )

    # studentGraduationGrade_id ["studentGraduationGrade_id"]
    mapping_values.append(
        check_ids(
            student_data,
            "studentGraduationGrade_id",
            "grades",
            university_education.studentGraduationGrade,
        )
    )

    # studentGraduationProjectGrade_id ["studentGraduationProjectGrade_id"]
    mapping_values.append(
        check_ids(
            student_data,
            "studentGraduationProjectGrade_id",
            "grades",
            university_education.studentGraduationProjectGrade,
        )
    )

    # studentRegistrationType_id ["RegistrationTypeID"]
    #   if `-1` expected to be `16`
    mapping_values.append(
        check_ids(
            student_data,
            "RegistrationTypeID",
            "registrationtype",
            university_education.studentRegistrationType,
        )
    )

    # studentLevel_id ["ConvertLevel"]
    mapping_values.append(
        check_ids(
            student_data,
            "ConvertLevel",
            "levels",
            university_education.studentLevel,
        )
    )

    # ----- * -----

    # studentTot ["studentTotalDegree"]
    mapping_values.append(
        (
            "studentTotalDegree",
            student_data.get("studentTotalDegree"),
            university_education.studentTot,
        )
    )

    # studentGraduationGPA ["studentGraduationGPA"]
    mapping_values.append(
        (
            "studentGraduationGPA",
            student_data.get("studentGraduationGPA"),
            university_education.studentGraduationGPA,
        )
    )

    # studentGraduationPercentage ["studentGraduationPercentage"]
    mapping_values.append(
        (
            "studentGraduationPercentage",
            student_data.get("studentGraduationPercentage"),
            university_education.studentGraduationPercentage,
        )
    )

    # studentDivision ["studentDivision"]
    mapping_values.append(
        (
            "studentDivision",
            student_data.get("studentDivision"),
            university_education.studentDivision,
        )
    )

    # studentSpecialization ["studentSpecialization"]
    mapping_values.append(
        (
            "studentSpecialization",
            student_data.get("studentSpecialization"),
            university_education.studentSpecialization,
        )
    )

    # totalEquivalentHours ["TotalEquivalentHours"]
    mapping_values.append(
        (
            "TotalEquivalentHours",
            student_data.get("TotalEquivalentHours"),
            university_education.totalEquivalentHours,
        )
    )

    # transferDate ["AcceptDate"] (-1 flag to transferred students)
    if student_data.get("RegistrationTypeID") == "-1":
        expected_date = re.search(
            ISODatePattern, student_data.get("AcceptDate", "")
        ).group(0)
        found = (
            str(university_education.transferDate)
            if university_education.transferDate
            else None
        )
        mapping_values.append(("AcceptDate", expected_date, found))

    # updatedAt ["ModifiedDate"] & updatedBy ["UserID"]
    mapping_values.extend(
        check_modification_info(
            student_data, university_education.updatedAt, university_education.updatedBy
        )
    )

    # ----- Compare values -----
    messages = compare_values(student_data, mapping_values, "university education")

    return messages


def check_ids(student_data, prop_key, mapping_key, prop):
    expected_id = student_data.get(prop_key)
    mapped_id = MAPPING_IDS.get(mapping_key).get(expected_id)
    return (prop_key, mapped_id, prop.id if prop else None)


def check_modification_info(student_data, actual_updated_at, actual_updated_by):
    mapping_values = []

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # updatedAt ["ModifiedDate"]
    updated_at = student_data.get("ModifiedDate")
    expected = str(datetime.strptime(updated_at, DATE_FORMAT)) if updated_at else None
    found = str(actual_updated_at)[:-6] if actual_updated_at else None
    mapping_values.append(("ModifiedDate", expected, found))

    # updatedBy ["UserID"]
    updated_by = student_data.get("UserID")
    mapped_user_id = MAPPING_IDS.get("users").get(updated_by)
    mapping_values.append(("UserID", mapped_user_id, actual_updated_by))

    return mapping_values


def compare_values(student_data, mapping_values, table):
    messages = []
    for item in mapping_values:
        prop, formatted, found = item
        if (formatted or None) != found:
            messages.append(
                create_mismatching_values_message(
                    table, prop, student_data.get(prop, None), formatted, found
                )
            )
    return messages


def extract_data_from_national_id(national_id):
    century = national_id[0:1]
    birth_year = "19" + national_id[1:3] if century == "2" else "20" + national_id[1:3]

    # studentBirthDate, YYYY-MM-DD
    birthdate = birth_year + "-" + national_id[3:5] + "-" + national_id[5:7]
    # studentGender_id, "0"->male | "1"->female (before mapping ids)
    gender_id = "0" if int(national_id[12:13]) % 2 != 0 else "1"

    return {"gender_id": gender_id, "birthdate": birthdate}


def create_mismatching_values_message(table, prop, received, formatted, found):
    return MESSAGES.get("MISMATCHING_VALUES").format(
        table=table, prop=prop, received=received, formatted=formatted, found=found
    )


def generate_report(old_council_id, student_data, status, errors=[]):
    return {
        "id": old_council_id,
        "status": status,
        "errors": errors,
        # "student": student_data,  # TODO: uncomment this line if needed
    }
