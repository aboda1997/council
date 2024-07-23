from django.db import transaction
from django.db.models import Exists, F, Subquery
from django.utils import timezone

from core.helpers.general import log_activity
from core.helpers.student_transactions import create_student_transactions
from core.helpers.students import (
    generate_student_unique_id,
    get_student_imposed_course_query,
    get_student_military_edu_query,
    get_student_query,
    get_student_sec_query,
    get_student_uni_query,
)
from core.helpers.students_validation import ValidationsRules
from core.models.db import Graduates, Years
from core.utils.enums import (
    CertificateEnum,
    CountryEnum,
    GenderEnum,
    RegistrationTypeEnum,
    StudentStatus,
)
from core.utils.exceptions import (
    InvalidParamsError,
    NotFoundError,
    UnprocessableParamsError,
)
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation


def validate_student(student_data, prev_student_data):
    student = student_data.get("student")
    student_sec_edu = student_data.get("studentSecondaryEdu")
    student_uni_edu = student_data.get("studentUniversityEdu")
    prev_student = prev_student_data.get("student")
    prev_student_sec_edu = prev_student_data.get("studentSecondaryEdu")
    prev_student_uni_edu = prev_student_data.get('studentUniversityEdu')

    # Not allow to set Student's Secondary Cert to Egyptian GS via this end point
    if str(student_sec_edu.get("studentSecondaryCert_id")) == str(
        CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
    ) and str(prev_student_sec_edu.get("studentSecondaryCert_id")) != str(
        CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
    ):
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_CERT_CHANGE"))

    # Egyptian GS Students cannot have their NID Changed
    is_incoming = str(
        prev_student_uni_edu.get("studentRegistrationType_id") or ""
    ) == str(RegistrationTypeEnum.INCOMING_STUDENTS.value)
    if (
        not is_incoming
        and prev_student.get("studentNID")
        and str(prev_student_sec_edu.get("studentSecondaryCert_id"))
        == str(CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value)
        and str(student.get("studentNID")) != str(prev_student.get("studentNID"))
    ):
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_NID_CHANGE"))

    student["studentName"] = " ".join(student.get("studentName").split())
    student_lang_names = (student.get("studentName") or "").split("|")
    student_ar_name = student_lang_names[0]
    student_en_name = student_lang_names[1] if len(student_lang_names) > 1 else ""
    min_names_parts_length = 4
    if (
        student.get("studentNationality_id")
        and int(student.get("studentNationality_id")) != CountryEnum.EGYPT.value
    ):
        min_names_parts_length = 2
    student_certificate = student_sec_edu.get(
        "studentSecondaryCert_id"
    ) or prev_student_sec_edu.get("studentSecondaryCert_id")
    student_status = StudentStatus.GRADUATE.value
    validation_rules = [
        *ValidationsRules.student_ar_name(student_ar_name, min_names_parts_length),
        *ValidationsRules.student_name(student_en_name, min_names_parts_length),
        *ValidationsRules.student_basic_data(student, False),
        *ValidationsRules.student_sec_edu_data(
            student_sec_edu, student_certificate, student_status
        ),
        *ValidationsRules.student_degree(student_sec_edu, student_certificate),
        *ValidationsRules.student_uni_edu_data(student_uni_edu),
        *ValidationsRules.graduation_data(student_uni_edu),
    ]
    Validation.run_validators_set(validation_rules)


def validate_student_db(student_data, prev_student_data):
    student = student_data.get("student")
    student_sec_edu = student_data.get("studentSecondaryEdu")
    prev_student = prev_student_data.get("student")
    national_no = None
    passport_no = None
    if (
        student.get("studentNationality_id")
        and int(student.get("studentNationality_id")) != CountryEnum.EGYPT.value
    ):
        passport_no = student.get("studentPassport")
    else:
        national_no = student.get("studentNID")

    # SubQueries are used to do a single query to database and thus lowering
    subqueries = {
        "military_edu_exists": Exists(
            get_student_military_edu_query(prev_student.get("id"), "graduate")
        ),
    }
    if national_no:
        subqueries["nid_exists"] = Exists(
            Graduates.objects.filter(
                studentNID__isnull=False, studentNID__exact=national_no
            ).exclude(id=prev_student.get("id"))
        )
    if passport_no:
        subqueries["passport_exists"] = Exists(
            Graduates.objects.filter(
                studentPassport__isnull=False,
                studentPassport__exact=passport_no,
                studentNationality_id__exact=student.get("studentNationality_id"),
            ).exclude(id=prev_student.get("id"))
        )
    if student_sec_edu.get("studentCertificateYear_id"):
        subqueries["cert_year_code"] = Subquery(
            Years.objects.filter(
                id=student_sec_edu.get("studentCertificateYear_id")
            ).values("code")[:1]
        )
    fk_data = (
        Years.objects.filter(current=1).values("code").annotate(**subqueries).first()
    )
    if not fk_data:
        raise InvalidParamsError(EXCEPTIONS.get("NO_CURRENT_YEAR"))
    if fk_data.get("nid_exists") is True:
        raise InvalidParamsError(EXCEPTIONS.get("CHECK_NATIONAL_ID_FAIL"))
    if fk_data.get('passport_exists') is True:
        raise InvalidParamsError(EXCEPTIONS.get('CHECK_PASSPORT_FAIL'))
    if fk_data.get("military_edu_exists") is True and (
        student.get("studentGender_id") != GenderEnum.MALE.value
        or (
            student.get("studentNationality_id")
            and student.get("studentNationality_id") != CountryEnum.EGYPT.value
        )
    ):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_MILITARY_INFO_CHANGE'))
    if student_sec_edu.get("studentCertificateYear_id") and int(
        fk_data.get("cert_year_code")
    ) > int(fk_data.get("code")):
        raise InvalidParamsError(EXCEPTIONS.get("LT_CURRENT_CERT_YEAR"))


def handle_invalid_fk(exception: Exception):
    exception_msg = str(exception)
    exception_dict = {
        "studentNationality_id": EXCEPTIONS.get("INVALID_NATIIONALITY_FK"),
        "studentAddressPlaceGov_id": EXCEPTIONS.get("INVALID_ADDRESS_GOVERNORATES_FK"),
        "studentBirthPlaceGov_id": EXCEPTIONS.get("INVALID_BIRTH_GOVERNORATES_FK"),
        'studentGender_id': EXCEPTIONS.get('INVALID_GENDER_FK'),
        "studentReligion_id": EXCEPTIONS.get("INVALID_RELIGION_FK"),
        "studentStatus_id": EXCEPTIONS.get("INVALID_STUDENT_STATUS_FK"),
        "studentCertificateYear_id": EXCEPTIONS.get("INVALID_CERT_YEAR_FK"),
        "studentSecondaryCert_id": EXCEPTIONS.get("INVALID_CERTIFICATE_FK"),
        "studentStudyGroup_id": EXCEPTIONS.get("INVALID_STUDY_GROUP_FK"),
        "studentFulfillment_id": EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
        "studentLevel_id": EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
        "transferFulfillment_id": EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
        "studentExpectedGraduationYear_id": EXCEPTIONS.get(
            "INVALID_GRADUATION_YEAR_FK"
        ),
        "studentExpectedGraduationMonth_id": EXCEPTIONS.get(
            "INVALID_GRADUATION_MONTH_FK"
        ),
        "studentGraduationGrade_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="graduation grade", keyAr="تقدير التخرج"
        ),
        "studentGraduationProjectGrade_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="graduation project grade", keyAr="تقدير مشروع التخرج"
        ),
        "studentActualGraduationYear_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="actual graduation year id", keyAr="عام التخرج"
        ),
        "studentActualGraduationMonth_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="actual graduation month id", keyAr="شهر التخرج"
        ),
    }
    for message_key in exception_dict:
        if "foreign key constraint" in exception_msg and message_key in exception_msg:
            raise UnprocessableParamsError(exception_dict.get(message_key))
    raise UnprocessableParamsError(EXCEPTIONS.get("EDIT_STUDENT_FAIL"))


def format_student(
    student_id: str,
    student_data: dict[str, any],
    prev_student_data: dict[str, any],
    user_id: str,
):
    prev_student = prev_student_data.get("student")
    prev_student_sec_edu = prev_student_data.get("studentSecondaryEdu")
    prev_student_uni_edu = prev_student_data.get('studentUniversityEdu')
    is_incoming = str(
        prev_student_uni_edu.get("studentRegistrationType_id") or ""
    ) == str(RegistrationTypeEnum.INCOMING_STUDENTS.value)
    updated_data = {
        "updatedAt": timezone.now(),
        "updatedBy": user_id,
    }
    student = student_data.get("student")
    formated_student = {**updated_data}
    student_sec_edu = student_data.get("studentSecondaryEdu")
    formated_student_sec_edu = {**updated_data}
    student_uni_edu = student_data.get("studentUniversityEdu")
    formated_student_uni_edu = {**updated_data}
    if student:
        formated_student = {
            **formated_student,
            "studentName": student.get("studentName", None),
            "studentNID": student.get("studentNID", None),
            "studentPassport": student.get("studentPassport", None),
            "studentBirthDate": student.get("studentBirthDate")
            if student.get("studentBirthDate")
            else None,
            "studentGender_id": student.get("studentGender_id", None),
            "studentBirthPlaceGov_id": student.get("studentBirthPlaceGov_id", None),
            "studentReligion_id": student.get("studentReligion_id", None),
            "studentAddressPlaceGov_id": student.get("studentAddressPlaceGov_id", None),
            "studentAddress": student.get("studentAddress", None),
            "studentPhone": student.get("studentPhone", None),
            "studentMail": student.get("studentMail", None),
            "notes": student.get("notes", None),
        }
        if student.get('studentNID') != prev_student.get('studentNID'):
            formated_student['studentNID'] = student.get('studentNID')
        if student.get('studentPassport') != prev_student.get('studentPassport'):
            formated_student['studentPassport'] = student.get('studentPassport')
        if not prev_student.get('uniqueId'):
            formated_student['uniqueId'] = generate_student_unique_id(
                prev_student.get("createdAt")
            )
        if (
            not is_incoming
            and not formated_student.get('studentNationality_id')
            or formated_student.get('studentNationality_id') == 1
        ):
            formated_student['studentPassport'] = None
        elif not is_incoming:
            formated_student['studentNID'] = None

    student_certificate = prev_student_sec_edu.get("studentSecondaryCert_id")
    if student_sec_edu:
        if student_certificate != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value:
            formated_student_sec_edu = {
                **formated_student_sec_edu,
                "studentSecondaryCert_id": student_sec_edu.get(
                    "studentSecondaryCert_id", None
                ),
                "studentCertificateYear_id": student_sec_edu.get(
                    "studentCertificateYear_id", None
                ),
                "studentStudyGroup_id": student_sec_edu.get(
                    "studentStudyGroup_id", None
                ),
                "studentTot": student_sec_edu.get("studentTot", None),
                "studentEquivTot": student_sec_edu.get("studentEquivTot", None),
            }
            formated_student_uni_edu = {
                **formated_student_uni_edu,
                "studentTot": student_sec_edu.get("studentEquivTot", None),
            }
        else:
            formated_student_sec_edu = {
                **formated_student_sec_edu,
                "studentSportDegree": student_sec_edu.get("studentSportDegree", None),
                "studentComplainGain": student_sec_edu.get("studentComplainGain", None),
            }

            degrees = [
                prev_student_sec_edu.get("studentTot", ""),
                student_sec_edu.get("studentSportDegree", ""),
                student_sec_edu.get("studentComplainGain", ""),
            ]
            updated_total_degree = 0
            for degree in degrees:
                try:
                    updated_total_degree += float(degree)
                except (Exception):
                    break
            if updated_total_degree:
                formated_student_uni_edu = {
                    **formated_student_uni_edu,
                    "studentTot": updated_total_degree,
                }

    student_uni_edu = student_data.get("studentUniversityEdu")
    if student_uni_edu:
        formated_student_uni_edu = {
            **formated_student_uni_edu,
            "studentExpectedGraduationYear_id": student_uni_edu.get(
                "studentExpectedGraduationYear_id", None
            ),
            "studentExpectedGraduationMonth_id": student_uni_edu.get(
                "studentExpectedGraduationMonth_id", None
            ),
            "studentGraduationGPA": student_uni_edu.get("studentGraduationGPA"),
            "studentGraduationGrade_id": student_uni_edu.get(
                "studentGraduationGrade_id"
            ),
            "studentGraduationPercentage": student_uni_edu.get(
                "studentGraduationPercentage"
            ),
            "studentGraduationEquivalentHours": student_uni_edu.get(
                "studentGraduationEquivalentHours"
            ),
            "studentSpecialization": student_uni_edu.get("studentSpecialization"),
            "studentDivision": student_uni_edu.get("studentDivision"),
            "studentGraduationProjectGrade_id": student_uni_edu.get(
                "studentGraduationProjectGrade_id"
            ),
            "studentActualGraduationYear_id": student_uni_edu.get(
                "studentActualGraduationYear_id"
            ),
            "studentActualGraduationMonth_id": student_uni_edu.get(
                "studentActualGraduationMonth_id"
            ),
        }
    if (
        prev_student_uni_edu.get('transferDate')
        or prev_student_uni_edu.get('studentRegistrationType_id')
        == RegistrationTypeEnum.TRANSFER.value
    ):
        formated_student_uni_edu = {
            **formated_student_uni_edu,
            'studentLevel_id': student_uni_edu.get('studentLevel_id', None),
            'totalEquivalentHours': student_uni_edu.get('totalEquivalentHours', None),
            'transferFulfillment_id': student_uni_edu.get(
                'transferFulfillment_id', None
            ),
        }
    return {
        "student": formated_student,
        "studentSecondaryEdu": formated_student_sec_edu,
        "studentUniversityEdu": formated_student_uni_edu,
    }


def edit_student(
    student_id: str, student_data: dict[str:any], request_summary: dict[str:any]
):
    user_id = request_summary.get("USER_ID")
    student_query = get_student_query(student_id, "graduate")
    student_sec_edu_query = get_student_sec_query(student_id, "graduate")
    student_uni_edu_query = get_student_uni_query(student_id, "graduate")
    student_imposed_course_query = get_student_imposed_course_query(
        student_id, "graduate"
    )
    prev_student = student_query.values().first()
    if not prev_student:
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    prev_student_sec_edu = (
        student_sec_edu_query.values()
        .annotate(studentCertificateYear__code=F("studentCertificateYear__code"))
        .first()
    )
    prev_student_uni_edu = student_uni_edu_query.values().first()
    prev_imposed_courses_data = list(student_imposed_course_query.values())
    prev_student_data = {
        "student": prev_student,
        "studentSecondaryEdu": prev_student_sec_edu,
        "studentUniversityEdu": prev_student_uni_edu,
        "studentImposedCourses": prev_imposed_courses_data,
    }
    student_data = format_student(
        student_id,
        student_data,
        prev_student_data,
        user_id,
    )
    validate_student(student_data, prev_student_data)
    validate_student_db(student_data, prev_student_data)
    log_activity("Editing Graduate Data", prev_student_data, request_summary)
    unique_id = prev_student.get("uniqueId")
    if not unique_id:
        unique_id = student_data.get('student').get("uniqueId")
    try:
        if prev_student_data:
            student_query.update(**student_data.get("student"))
        if prev_student_sec_edu:
            student_sec_edu_query.update(**student_data.get("studentSecondaryEdu"))
        if prev_student_uni_edu:
            student_uni_edu_query.update(**student_data.get("studentUniversityEdu"))
        # create student transaction
        create_student_transactions(user_id, unique_id, prev_student_data, student_data)
        return MESSAGES.get("EDIT_STUDENT_SUCCESS")
    except (Exception) as ex:
        handle_invalid_fk(ex)


def delete_student(student_id: str, request_summary: dict[str:any]):
    student_basic_query = get_student_query(student_id, "graduate")
    student_sec_edu_query = get_student_sec_query(student_id, "graduate")
    student_uni_edu_query = get_student_uni_query(student_id, "graduate")
    student_military_edu_query = get_student_military_edu_query(student_id, "graduate")
    imposed_courses_query = get_student_imposed_course_query(student_id, "graduate")
    if not student_basic_query.exists():
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    prev_student_data = {
        "student": student_basic_query.values().first(),
        "studentSecondaryEdu": student_sec_edu_query.values().first(),
        "studentUniversityEdu": student_uni_edu_query.values().first(),
        "studentMilitaryEdu": student_military_edu_query.values().first(),
        "studentImposedCourses": list(imposed_courses_query.values()),
    }
    log_activity("Deleting Graduate Data", prev_student_data, request_summary)
    try:
        with transaction.atomic():
            student_basic_query.delete()
            student_sec_edu_query.delete()
            student_uni_edu_query.delete()
            student_military_edu_query.delete()
            imposed_courses_query.delete()
        return MESSAGES.get("DELETE_STUDENT_SUCCESS")
    except (Exception):
        raise UnprocessableParamsError(EXCEPTIONS.get("DELETE_STUDENT_FAIL"))
