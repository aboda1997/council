import json

from django.db import DatabaseError, transaction
from django.db.models import Exists, F, Subquery
from django.utils import timezone

from core.helpers.general import log_activity
from core.helpers.search import create_arabic_format
from core.helpers.student_transactions import (
    create_imposed_courses_transaction,
    create_manual_add_student_transaction,
    create_student_transactions,
)
from core.helpers.students import (
    can_revert_transaction,
    generate_student_unique_id,
    get_student_imposed_course_query,
    get_student_military_edu_query,
    get_student_query,
    get_student_sec_query,
    get_student_uni_query,
)
from core.helpers.students_validation import ValidationsRules
from core.models.db import (
    Faculties,
    Regions,
    Students,
    StudentsImposedCourses,
    StudentsSecondaryEdu,
    StudentsTransactions,
    StudentsUniversityEdu,
    Universities,
    Years,
)
from core.models.gsdb import StageNew
from core.utils.enums import (
    CertificateEnum,
    CountryEnum,
    GenderEnum,
    RegistrationTypeEnum,
    StudentStatus,
    TransactionsTypeEnum,
    UniversityIdEnum,
    UniversityTypeEnum,
)
from core.utils.exceptions import (
    InvalidParamsError,
    NotFoundError,
    UnprocessableParamsError,
)
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation


def adjust_filters(filters):
    allowed_search_status = []
    for status in filters["status"]:
        if status.get("id") not in [StudentStatus.GRADUATE.value]:
            allowed_search_status.append(status)
    filters["status"] = allowed_search_status
    return filters


def adjust_form_filters(filters):
    filters["universities"] = list(
        Universities.objects.exclude(
            typeid__in=[
                UniversityTypeEnum.COUNCIL.value,
                UniversityTypeEnum.INSTITUTE.value,
            ]
        ).values("id", "name", "gov", "typeid", "type")
    )
    return filters


def validate_student(student_data, prev_student_data):
    student = student_data.get('student')
    student_sec_edu = student_data.get('studentSecondaryEdu')
    student_uni_edu = student_data.get('studentUniversityEdu')
    prev_student = prev_student_data.get('student')
    prev_student_sec_edu = prev_student_data.get('studentSecondaryEdu')
    prev_student_uni_edu = prev_student_data.get('studentUniversityEdu')

    # No changes are allowed if the students status remains INITIALLY_ACCEPTED
    # But this condition allows the status to be set back to INITIALLY_ACCEPTED
    if str(prev_student.get('studentStatus_id')) == str(
        StudentStatus.INITIALLY_ACCEPTED.value
    ) and str(student.get('studentStatus_id')) == str(
        StudentStatus.INITIALLY_ACCEPTED.value
    ):
        raise InvalidParamsError(EXCEPTIONS.get('STUDENT_STATUS_EDIT_NOT_ALLOWED'))

    if str(prev_student.get('studentStatus_id')) == str(
        StudentStatus.WITHDRAWN.value
    ) and str(student.get('studentStatus_id')) not in [
        str(StudentStatus.ACCEPTED.value),
        str(StudentStatus.FULFILLMENT.value),
        str(StudentStatus.WITHDRAWN.value),
    ]:
        raise InvalidParamsError(EXCEPTIONS.get('STUDENT_STATUS_CHANGE_NOT_ALLOWED'))

    if str(prev_student.get('studentStatus_id')) != str(
        student.get('studentStatus_id')
    ) and str(student.get('studentStatus_id')) in [
        str(StudentStatus.TRANSFERRED.value),
        str(StudentStatus.GRADUATION_APPLICANT.value),
        str(StudentStatus.GRADUATE.value),
    ]:
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_STATUS_ID_CHANGE'))

    # This is not to no allow setting Student's Secondary Cert to Egyptian GS via the end end point
    if str(student_sec_edu.get('studentSecondaryCert_id')) == str(
        CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
    ) and str(prev_student_sec_edu.get('studentSecondaryCert_id')) != str(
        CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
    ):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_CERT_CHANGE'))

    # Egyptian GS Students cannot have their NID Changed
    is_incoming = str(
        prev_student_uni_edu.get("studentRegistrationType_id") or ""
    ) == str(RegistrationTypeEnum.INCOMING_STUDENTS.value)
    if (
        not is_incoming
        and student.get('studentNID')
        and prev_student.get('studentNID')
        and str(prev_student_sec_edu.get('studentSecondaryCert_id'))
        == str(CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value)
        and str(student.get('studentNID')) != str(prev_student.get('studentNID'))
    ):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_NID_CHANGE'))

    student['studentName'] = ' '.join(student.get('studentName').split())
    student_lang_names = (student.get('studentName') or '').split('|')
    student_ar_name = student_lang_names[0]
    student_en_name = student_lang_names[1] if len(student_lang_names) > 1 else ''
    min_names_parts_length = 4
    if (
        not student.get("studentNationality_id")
        or int(student.get("studentNationality_id")) != CountryEnum.EGYPT.value
    ):
        min_names_parts_length = 2
    student_certificate = student_sec_edu.get(
        'studentSecondaryCert_id'
    ) or prev_student_sec_edu.get('studentSecondaryCert_id')
    student_status = student.get('studentStatus_id')
    validation_rules = [
        *ValidationsRules.student_ar_name(student_ar_name, min_names_parts_length),
        *ValidationsRules.student_name(student_en_name, min_names_parts_length),
        *ValidationsRules.student_basic_data(student),
        *ValidationsRules.student_sec_edu_data(
            student_sec_edu, student_certificate, student_status
        ),
        *ValidationsRules.student_degree(student_sec_edu, student_certificate),
        *ValidationsRules.student_uni_edu_data(student_uni_edu),
    ]
    Validation.run_validators_set(validation_rules)


def validate_student_db(student_data, prev_student_data):
    student = student_data.get('student')
    student_sec_edu = student_data.get('studentSecondaryEdu')
    prev_student = prev_student_data.get('student')
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
            get_student_military_edu_query(prev_student.get("id"))
        ),
    }
    if national_no:
        subqueries['nid_exists'] = Exists(
            Students.objects.filter(
                studentNID__isnull=False, studentNID__exact=national_no
            ).exclude(id=prev_student.get("id"))
        )
    if passport_no:
        subqueries['passport_exists'] = Exists(
            Students.objects.filter(
                studentPassport__isnull=False,
                studentPassport__exact=passport_no,
                studentNationality_id__exact=student.get('studentNationality_id'),
            ).exclude(id=prev_student.get("id"))
        )
    if student_sec_edu.get("studentCertificateYear_id"):
        subqueries['cert_year_code'] = Subquery(
            Years.objects.filter(
                id=student_sec_edu.get("studentCertificateYear_id")
            ).values('code')[:1]
        )
    fk_data = (
        Years.objects.filter(current=1).values('code').annotate(**subqueries).first()
    )
    if not fk_data:
        raise InvalidParamsError(EXCEPTIONS.get('NO_CURRENT_YEAR'))
    if fk_data.get('nid_exists') is True:
        raise InvalidParamsError(EXCEPTIONS.get('CHECK_NATIONAL_ID_FAIL'))
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
        fk_data.get('cert_year_code')
    ) > int(fk_data.get('code')):
        raise InvalidParamsError(EXCEPTIONS.get('LT_CURRENT_CERT_YEAR'))


def handle_invalid_fk(exception: Exception):
    exception_msg = str(exception)
    exception_dict = {
        'studentNationality_id': EXCEPTIONS.get('INVALID_NATIIONALITY_FK'),
        'studentAddressPlaceGov_id': EXCEPTIONS.get('INVALID_ADDRESS_GOVERNORATES_FK'),
        'studentBirthPlaceGov_id': EXCEPTIONS.get('INVALID_BIRTH_GOVERNORATES_FK'),
        'studentGender_id': EXCEPTIONS.get('INVALID_GENDER_FK'),
        'studentReligion_id': EXCEPTIONS.get('INVALID_RELIGION_FK'),
        'studentStatus_id': EXCEPTIONS.get('INVALID_STUDENT_STATUS_FK'),
        'studentCertificateYear_id': EXCEPTIONS.get('INVALID_CERT_YEAR_FK'),
        'studentSecondaryCert_id': EXCEPTIONS.get('INVALID_CERTIFICATE_FK'),
        'studentStudyGroup_id': EXCEPTIONS.get('INVALID_STUDY_GROUP_FK'),
        'studentFulfillment_id': EXCEPTIONS.get('INVALID_FULFILLMENT_FK'),
        'studentExpectedGraduationYear_id': EXCEPTIONS.get(
            'INVALID_GRADUATION_YEAR_FK'
        ),
        'studentExpectedGraduationMonth_id': EXCEPTIONS.get(
            'INVALID_GRADUATION_MONTH_FK'
        ),
        "studentLevel_id": EXCEPTIONS.get("INVALID_TRANSFER_LEVEL"),
        "transferFulfillment_id": EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
    }
    for message_key in exception_dict:
        if 'foreign key constraint' in exception_msg and message_key in exception_msg:
            raise UnprocessableParamsError(exception_dict.get(message_key))
    raise UnprocessableParamsError(EXCEPTIONS.get('EDIT_STUDENT_FAIL'))


def get_existant_imposed_course(course_id: int, prev_courses: list[dict:any]):
    for course in prev_courses:
        if course.get("imposedCourse_id") == course_id:
            return course
    return None


def format_student(
    student_id: str,
    student_data: dict[str, any],
    prev_student_data: dict[str, any],
    user_id: str,
):
    prev_student = prev_student_data.get('student')
    prev_student_sec_edu = prev_student_data.get('studentSecondaryEdu')
    prev_student_uni_edu = prev_student_data.get('studentUniversityEdu')
    is_incoming = str(
        prev_student_uni_edu.get("studentRegistrationType_id") or ""
    ) == str(RegistrationTypeEnum.INCOMING_STUDENTS.value)
    updated_data = {
        'updatedAt': timezone.now(),
        'updatedBy': user_id,
    }
    student = student_data.get('student')
    formated_student = {**updated_data}
    student_sec_edu = student_data.get('studentSecondaryEdu')
    formated_student_sec_edu = {**updated_data}
    student_uni_edu = student_data.get('studentUniversityEdu')
    formated_student_uni_edu = {**updated_data}
    if student:
        formated_student = {
            **formated_student,
            'studentName': student.get('studentName', None),
            'studentNationality_id': student.get('studentNationality_id', None),
            'studentBirthDate': student.get('studentBirthDate')
            if student.get('studentBirthDate')
            else None,
            'studentGender_id': student.get('studentGender_id', None),
            'studentBirthPlaceGov_id': student.get('studentBirthPlaceGov_id', None),
            'studentReligion_id': student.get('studentReligion_id', None),
            'studentAddressPlaceGov_id': student.get('studentAddressPlaceGov_id', None),
            'studentAddress': student.get('studentAddress', None),
            'studentPhone': student.get('studentPhone', None),
            'studentMail': student.get('studentMail', None),
            'studentStatus_id': student.get('studentStatus_id', None),
            'notes': student.get('notes', None),
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

    if (
        student_sec_edu
        and student.get("studentStatus_id") == StudentStatus.FULFILLMENT.value
    ):
        formated_student_sec_edu = {
            **formated_student_sec_edu,
            'studentFulfillment_id': student_sec_edu.get('studentFulfillment_id', None),
        }
    student_certificate = prev_student_sec_edu.get("studentSecondaryCert_id")
    if student_sec_edu:
        if student_certificate != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value:
            formated_student_sec_edu = {
                **formated_student_sec_edu,
                'studentSecondaryCert_id': student_sec_edu.get(
                    'studentSecondaryCert_id', None
                ),
                'studentCertificateYear_id': student_sec_edu.get(
                    'studentCertificateYear_id', None
                ),
                'studentStudyGroup_id': student_sec_edu.get(
                    'studentStudyGroup_id', None
                ),
                'studentTot': student_sec_edu.get('studentTot', None),
                'studentEquivTot': student_sec_edu.get('studentEquivTot', None),
            }
            formated_student_uni_edu = {
                **formated_student_uni_edu,
                'studentTot': student_sec_edu.get('studentEquivTot', None),
            }
        else:
            formated_student_sec_edu = {
                **formated_student_sec_edu,
                'studentSportDegree': student_sec_edu.get('studentSportDegree', None),
                'studentComplainGain': student_sec_edu.get('studentComplainGain', None),
            }

            degrees = [
                prev_student_sec_edu.get('studentTot', ''),
                student_sec_edu.get('studentSportDegree', ''),
                student_sec_edu.get('studentComplainGain', ''),
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
                    'studentTot': updated_total_degree,
                }

    student_uni_edu = student_data.get('studentUniversityEdu')
    if student_uni_edu:
        formated_student_uni_edu = {
            **formated_student_uni_edu,
            'studentExpectedGraduationYear_id': student_uni_edu.get(
                'studentExpectedGraduationYear_id', None
            ),
            'studentExpectedGraduationMonth_id': student_uni_edu.get(
                'studentExpectedGraduationMonth_id', None
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

    prev_student_imposed_courses = prev_student_data.get('studentImposedCourses')
    student_imposed_courses = student_data.get('studentImposedCourses')
    imposed_course_list = []
    if student_imposed_courses:
        for course in student_imposed_courses:
            course_values = {
                'createdBy': user_id,
                'student_id': student_id,
                'imposedCourse_id': course.get('imposedCourse_id'),
                'completed': course.get('completed') or False,
            }
            prev_course = get_existant_imposed_course(
                course.get('imposedCourse_id'), prev_student_imposed_courses
            )
            if prev_course:
                course_values = {
                    **course_values,
                    **updated_data,
                    'createdAt': prev_course.get("createdAt"),
                    'createdBy': prev_course.get("createdBy"),
                }
            imposed_course_list.append(
                StudentsImposedCourses(
                    **course_values,
                )
            )
    return {
        'student': formated_student,
        'studentSecondaryEdu': formated_student_sec_edu,
        'studentUniversityEdu': formated_student_uni_edu,
        'studentImposedCourses': imposed_course_list,
    }


def edit_student(
    student_id: str, student_data: dict[str:any], request_summary: dict[str:any]
):
    user_id = request_summary.get("USER_ID")
    student_query = get_student_query(student_id)
    student_sec_edu_query = get_student_sec_query(student_id)
    student_uni_edu_query = get_student_uni_query(student_id)
    student_imposed_course_query = get_student_imposed_course_query(student_id)
    prev_student = student_query.values().first()
    prev_student_sec_edu = (
        student_sec_edu_query.values()
        .annotate(studentCertificateYear__code=F('studentCertificateYear__code'))
        .first()
    )
    prev_student_uni_edu = student_uni_edu_query.values().first()
    prev_imposed_courses_data = list(student_imposed_course_query.values())
    prev_student_data = {
        'student': prev_student,
        'studentSecondaryEdu': prev_student_sec_edu,
        'studentUniversityEdu': prev_student_uni_edu,
        'studentImposedCourses': prev_imposed_courses_data,
    }
    imposed_courses_ids = []
    for course in student_data.get('studentImposedCourses'):
        imposed_courses_ids.append(course.get('imposedCourse_id'))
    imposed_courses_ids = sorted(imposed_courses_ids)
    prev_imposed_courses = sorted(
        list(student_imposed_course_query.values_list("imposedCourse_id", flat=True))
    )
    imposed_courses_changed = prev_imposed_courses != imposed_courses_ids

    student_data = format_student(
        student_id,
        student_data,
        prev_student_data,
        user_id,
    )
    unique_id = prev_student.get("uniqueId")
    if not unique_id:
        unique_id = student_data.get('student').get("uniqueId")
    validate_student(student_data, prev_student_data)
    validate_student_db(student_data, prev_student_data)
    log_activity("Editing Student Data", prev_student_data, request_summary)
    try:
        with transaction.atomic():
            if prev_student:
                student_query.update(**student_data.get('student'))
            if prev_student_sec_edu:
                student_sec_edu_query.update(**student_data.get('studentSecondaryEdu'))
            if prev_student_uni_edu:
                student_uni_edu_query.update(**student_data.get('studentUniversityEdu'))

            student_imposed_course_query.delete()
            StudentsImposedCourses.objects.bulk_create(
                student_data.get('studentImposedCourses')
            )

            # create student transaction
            create_student_transactions(
                user_id, unique_id, prev_student_data, student_data
            )
            if imposed_courses_changed:
                create_imposed_courses_transaction(
                    user_id, unique_id, prev_imposed_courses, imposed_courses_ids
                )

        return MESSAGES.get('EDIT_STUDENT_SUCCESS')
    except DatabaseError as ex:
        handle_invalid_fk(ex)


def delete_student(student_id: str, request_summary: dict[str:any]):
    student_basic_query = get_student_query(student_id)
    student_sec_edu_query = get_student_sec_query(student_id)
    student_uni_edu_query = get_student_uni_query(student_id)
    student_military_edu_query = get_student_military_edu_query(student_id)
    imposed_courses_query = get_student_imposed_course_query(student_id)
    if not student_basic_query.exists():
        raise NotFoundError(EXCEPTIONS.get('STUDENT_DOES_NOT_EXIST'))
    prev_student_data = {
        'student': student_basic_query.values().first(),
        'studentSecondaryEdu': student_sec_edu_query.values().first(),
        'studentUniversityEdu': student_uni_edu_query.values().first(),
        'studentMilitaryEdu': student_military_edu_query.values().first(),
        'studentImposedCourses': list(imposed_courses_query.values()),
    }
    log_activity("Deleting Student Data", prev_student_data, request_summary)
    try:
        with transaction.atomic():
            student_basic_query.delete()
            student_sec_edu_query.delete()
            student_uni_edu_query.delete()
            student_military_edu_query.delete()
            imposed_courses_query.delete()
        return MESSAGES.get('DELETE_STUDENT_SUCCESS')
    except (Exception):
        raise UnprocessableParamsError(EXCEPTIONS.get('DELETE_STUDENT_FAIL'))


#  LOGIC related to add a new student
def format_add_student(student_data: dict[str:any], user_id: str):
    created_data = {
        "createdAt": timezone.now(),
        "createdBy": user_id,
    }
    student: dict[str:any] = student_data.get("student")
    formated_student = {**created_data}
    student_sec_edu: dict[str:any] = student_data.get("studentSecondaryEdu")
    formated_student_sec_edu = {**created_data}
    student_uni_edu = student_data.get("studentUniversityEdu")
    formated_student_uni_edu: dict[str:any] = {**created_data}

    if student:
        formated_student = {
            **formated_student,
            "studentName": student.get("studentName", None),
            "studentNationality_id": student.get("studentNationality_id", None),
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
            "studentStatus_id": student.get("studentStatus_id", None),
            "notes": student.get("notes", None),
            "uniqueId": generate_student_unique_id(formated_student.get("createdAt")),
        }
    if student_sec_edu:
        formated_student_sec_edu = {
            "studentSecondaryCert_id": student_sec_edu.get(
                "studentSecondaryCert_id", None
            ),
            "studentCertificateYear_id": student_sec_edu.get(
                "studentCertificateYear_id", None
            ),
            "studentStudyGroup_id": student_sec_edu.get("studentStudyGroup_id", None),
        }
        if (
            student_sec_edu.get("studentSecondaryCert_id", None)
            != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
        ):
            formated_student_sec_edu = {
                **formated_student_sec_edu,
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
                "studentSeatNumber": student_sec_edu.get("studentSeatNumber", None),
                "studentTot": student_sec_edu.get("studentTot", None),
                "studentSportDegree": student_sec_edu.get("studentSportDegree", None),
                "studentComplainGain": student_sec_edu.get("studentComplainGain", None),
            }

            degrees = [
                student_sec_edu.get("studentTot", ""),
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
    if (
        student_sec_edu
        and student.get("studentStatus_id") == StudentStatus.FULFILLMENT.value
    ):
        formated_student_sec_edu = {
            **formated_student_sec_edu,
            'studentFulfillment_id': student_sec_edu.get('studentFulfillment_id', None),
        }
    if student_uni_edu:
        formated_student_uni_edu = {
            **formated_student_uni_edu,
            "studentRegistrationType_id": RegistrationTypeEnum.PRIMARY.value,
            "studentEnrollYear_id": student_uni_edu.get("studentEnrollYear_id", None),
            "studentEnrollSemester_id": student_uni_edu.get(
                "studentEnrollSemester_id", None
            ),
            "studentEnrollStage_id": student_uni_edu.get("studentEnrollStage_id", None),
            "studentUniveristy_id": student_uni_edu.get("studentUniveristy_id", None),
            "studentFaculty_id": student_uni_edu.get("studentFaculty_id", None),
            "studentExpectedGraduationYear_id": student_uni_edu.get(
                "studentExpectedGraduationYear_id", None
            ),
            "studentExpectedGraduationMonth_id": student_uni_edu.get(
                "studentExpectedGraduationMonth_id", None
            ),
        }
        if (
            student_uni_edu.get("studentUniveristy_id", None)
            == UniversityIdEnum.EXTERNAL.value
        ):
            formated_student_uni_edu[
                "studentCustomUniversityFaculty"
            ] = student_uni_edu.get("studentCustomUniversityFaculty")
            del formated_student_uni_edu["studentFaculty_id"]
    return {
        "student": formated_student,
        "studentSecondaryEdu": formated_student_sec_edu,
        "studentUniversityEdu": formated_student_uni_edu,
    }


def validate_add_student(student_data):
    student = student_data.get("student")
    student_sec_edu = student_data.get("studentSecondaryEdu")
    student_uni_edu = student_data.get("studentUniversityEdu")

    if str(student.get("studentStatus_id")) in [
        str(StudentStatus.INITIALLY_ACCEPTED.value),
        str(StudentStatus.TRANSFERRED.value),
        str(StudentStatus.GRADUATION_APPLICANT.value),
        str(StudentStatus.GRADUATE.value),
    ]:
        raise InvalidParamsError(EXCEPTIONS.get("NOT_ALLOWED_ADD_STUDENT_STATUS"))
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
    student_certificate = student_sec_edu.get("studentSecondaryCert_id")
    student_status = student.get("studentStatus_id")
    validation_rules = [
        *ValidationsRules.student_ar_name(student_ar_name, min_names_parts_length),
        *ValidationsRules.student_name(student_en_name, min_names_parts_length),
        *ValidationsRules.student_basic_data(student),
        *ValidationsRules.add_student_sec_edu_data(student_sec_edu),
        *ValidationsRules.student_sec_edu_data(
            student_sec_edu, student_certificate, student_status
        ),
        *ValidationsRules.student_degree(student_sec_edu, student_certificate),
        *ValidationsRules.add_student_uni_edu_data(student_uni_edu),
        *ValidationsRules.student_uni_edu_data(student_uni_edu),
    ]
    Validation.run_validators_set(validation_rules)


def validate_add_student_db(student_data):
    student = student_data.get("student")
    student_sec_edu = student_data.get("studentSecondaryEdu")
    student_uni_edu = student_data.get("studentUniversityEdu")
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
        "facultyUniversity_id": Faculties.objects.filter(
            id=student_uni_edu.get("studentFaculty_id")
        ).values("univ_id")[:1]
    }
    if national_no:
        subqueries["nid_exists"] = Exists(
            Students.objects.filter(
                studentNID__isnull=False, studentNID__exact=national_no
            )
        )
    if passport_no:
        subqueries["passport_exists"] = Exists(
            Students.objects.filter(
                studentPassport__isnull=False,
                studentPassport__exact=passport_no,
                studentNationality_id__exact=student.get("studentNationality_id"),
            )
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
    if fk_data.get("passport_exists") is True:
        raise InvalidParamsError(EXCEPTIONS.get("CHECK_PASSPORT_FAIL"))
    if fk_data.get("military_edu_exists") is True and (
        student.get("studentGender_id") != GenderEnum.MALE.value
        or (
            student.get("studentNationality_id")
            and student.get("studentNationality_id") != CountryEnum.EGYPT.value
        )
    ):
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_MILITARY_INFO_CHANGE"))
    if student_sec_edu.get("studentCertificateYear_id") and int(
        fk_data.get("cert_year_code")
    ) > int(fk_data.get("code")):
        raise InvalidParamsError(EXCEPTIONS.get("LT_CURRENT_CERT_YEAR"))
    if str(student_uni_edu.get("studentUniveristy_id")) != str(
        UniversityIdEnum.EXTERNAL.value
    ) and str(student_uni_edu.get("studentUniveristy_id")) != str(
        fk_data.get("facultyUniversity_id")
    ):
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_FACULTY_UNIV_NOT_MATCH"))


def add_student(student_data: dict[str:any], request_summary: dict[str:any]):
    student_data = format_add_student(student_data, request_summary.get("USER_ID"))
    validate_add_student(student_data)
    validate_add_student_db(student_data)
    try:
        student = Students(**student_data.get("student"))
        student.save()
        student_data["studentSecondaryEdu"]["student_id"] = student.id
        student_data["studentUniversityEdu"]["student_id"] = student.id
        StudentsSecondaryEdu(**student_data.get("studentSecondaryEdu")).save()
        StudentsUniversityEdu(**student_data.get("studentUniversityEdu")).save()
        create_manual_add_student_transaction(
            request_summary.get("USER_ID"), student.uniqueId
        )
        return MESSAGES.get("ADD_STUDENT_SUCCESS")
    except (Exception):
        raise UnprocessableParamsError(EXCEPTIONS.get("ADD_STUDENT_FAIL"))


# Gets the secondary gs info from the gs db
def validate_secondary_gs_request(nid: int, certificate: int, cert_year: int):
    validation_rules = [
        *ValidationsRules.national_id(nid, required=True),
        *ValidationsRules.database_id(
            certificate,
            "Secondary certificate",
            "شهادة الثانوية",
            required=True,
        ),
        *ValidationsRules.database_id(
            cert_year,
            "Secondary certificate year",
            "عام الحصول على الشهادة الثانوية",
            required=True,
        ),
    ]
    Validation.run_validators_set(validation_rules)


def format_secondary_gs_info(student_data: dict[str:any]):
    formalized_basic_student = {
        "studentName": student_data.get("arabic_name", None),
        "studentNID": student_data.get("national_no", None),
        "studentGender_id": student_data.get("gender_id", None),
        "studentReligion_id": student_data.get("religion_id", None),
        "studentBirthPlaceGov_id": student_data.get("birth_id", None),
        "studentAddressPlaceGov_id": student_data.get("city_id", None),
        "studentAddress": student_data.get("address", None),
    }
    formalized_student_sec_edu = {
        "studentSecondaryCert_id": student_data.get("certificate", None),
        "studentCertificateYear_id": student_data.get("certYear", None),
        "studentStudyGroup_id": student_data.get("branch_code_new", None),
        "studentSeatNumber": student_data.get("seating_no", None),
        "studentTot": student_data.get("total_degree", None),
    }
    return {
        "student": formalized_basic_student,
        "studentSecondaryEdu": formalized_student_sec_edu,
    }


def get_secondary_gs_info(nid: int, certificate: int, cert_year: int):
    validate_secondary_gs_request(nid, certificate, cert_year)

    if int(certificate) != CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value:
        raise UnprocessableParamsError(EXCEPTIONS.get("NOT_GS_CERTIFICATE"))

    year = Years.objects.filter(id=cert_year).values("code").first()
    if not year:
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_CERT_YEAR_FK"))

    year_code = str(year.get("code"))
    db_name = "gs_" + year_code
    try:
        student_data = (
            StageNew.objects.filter(national_no__exact=nid)
            .values(
                "seating_no",
                "national_no",
                "arabic_name",
                "gender_id",
                "religion_id",
                "total_degree",
                "branch_code_new",
                "city_name",
                "birth_palace",
                "address",
            )
            .using(db_name)
            .first()
        )
    except Exception as exception:
        if f"The connection '{db_name}' doesn't exist." == str(exception):
            raise NotFoundError(EXCEPTIONS.get('MISSING_GS_CD'))
    if not student_data:
        raise NotFoundError(EXCEPTIONS.get('GS_STUDENT_NOT_FOUND'))

    student_data["certificate"] = int(certificate)
    student_data["certYear"] = int(cert_year)

    if student_data.get("branch_code_new"):
        mapping_gs_to_council = {
            0: None,
            1: 1,
            2: 2,
            5: 3,
            4: 4,
        }
        student_data["branch_code_new"] = mapping_gs_to_council.get(
            student_data.get("branch_code_new")
        )

    if student_data.get("city_name"):
        current_city = (
            Regions.objects.filter(
                name__iregex=create_arabic_format(student_data.get("city_name")),
                typeid="2",
            )
            .values("id")
            .first()
        )
        student_data["city_id"] = current_city.get("id") if current_city else None

    if student_data.get("birth_palace"):
        birth_city = (
            Regions.objects.filter(
                name__iregex=create_arabic_format(student_data.get("birth_palace")),
                typeid="2",
            )
            .values("id")
            .first()
        )
        student_data["birth_id"] = birth_city.get("id") if birth_city else None

    student_data = format_secondary_gs_info(student_data)
    return student_data


# LOGIC related to revert transactions
def format_revert_transcation(transaction_data: dict[str:any], user_id: str):
    updated_data = {
        'updatedAt': timezone.now(),
        'updatedBy': user_id,
    }
    formated_student = {**updated_data}
    if transaction_data.get("studentStatus_id"):
        formated_student["studentStatus_id"] = transaction_data.get("studentStatus_id")
    formated_student_uni_edu = {
        **updated_data,
        "studentUniveristy_id": transaction_data.get("studentUniveristy_id")
        or transaction_data.get("Univeristy_id"),
        "studentFaculty_id": transaction_data.get("studentFaculty_id")
        or transaction_data.get("Faculty_id"),
        "studentEnrollYear_id": transaction_data.get("studentEnrollYear_id")
        or transaction_data.get("EnrollYear_id"),
        "studentEnrollSemester_id": transaction_data.get("studentEnrollSemester_id")
        or transaction_data.get("EnrollSemester_id"),
        "studentEnrollStage_id": transaction_data.get("studentEnrollStage_id")
        or transaction_data.get("EnrollStage_id"),
        "studentRegistrationType_id": transaction_data.get("RegistrationType_id"),
        "studentLevel_id": transaction_data.get("studentLevel_id")
        or transaction_data.get("Level_id"),
        "totalEquivalentHours": transaction_data.get("totalEquivalentHours"),
        "transferDate": transaction_data.get("transferDate"),
    }
    return {
        "student": formated_student,
        "studentUniversityEdu": formated_student_uni_edu,
    }


def format_new_original_transcation(
    prev_student_data: dict[str:any], transaction_data: dict[str:any]
):
    prev_student = prev_student_data.get("student")
    prev_student_uni = prev_student_data.get("studentUniversityEdu")
    new_original = {}
    if transaction_data.get("studentStatus_id"):
        new_original["studentStatus_id"] = prev_student.get("studentStatus_id")
    original_date = (
        str(prev_student_uni.get("transferDate"))
        if prev_student_uni.get("transferDate")
        else None
    )
    new_original = {
        **new_original,
        "Univeristy_id": prev_student_uni.get("studentUniveristy_id"),
        "Faculty_id": prev_student_uni.get("studentFaculty_id"),
        "EnrollYear_id": prev_student_uni.get("studentEnrollYear_id"),
        "EnrollSemester_id": prev_student_uni.get("studentEnrollSemester_id"),
        "EnrollStage_id": prev_student_uni.get("studentEnrollStage_id"),
        "RegistrationType_id": prev_student_uni.get("studentRegistrationType_id"),
        "studentLevel_id": prev_student_uni.get("studentLevel_id"),
        "totalEquivalentHours": prev_student_uni.get("totalEquivalentHours"),
        "transferDate": original_date,
    }
    return new_original


def revert_transcations(
    student_id: str, transaction_id: str, request_summary: dict[str:any]
):
    student_query = get_student_query(student_id)
    student_uni_edu_query = get_student_uni_query(student_id)
    student_data = student_query.values().first()
    if not student_data:
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    prev_student_data = {
        "student": student_data,
        "studentUniversityEdu": student_uni_edu_query.values().first(),
    }
    transaction_data = (
        StudentsTransactions.objects.filter(id=transaction_id).values().first()
    )
    if not transaction_data:
        raise NotFoundError(EXCEPTIONS.get("TRANSACTION_DOES_NOT_EXIST"))
    if student_data.get("uniqueId") != transaction_data.get("uniqueId"):
        raise UnprocessableParamsError(EXCEPTIONS.get("TRANSACTION_NOT_BELONG_STUDENT"))
    if transaction_data.get("transactionType_id") not in [
        TransactionsTypeEnum.TRANSFER_FACULTY.value,
        TransactionsTypeEnum.PATH_SHIFT.value,
        TransactionsTypeEnum.WITHDRAW_BY_OLD_COUNCIL.value,
        TransactionsTypeEnum.DATA_FROM_OLD_SYSTEM.value,
        TransactionsTypeEnum.REVERT_STUDENT_DATA.value,
    ]:
        raise UnprocessableParamsError(EXCEPTIONS.get("NOT_TRANSACTION_TRANSFER"))
    original_data = {}
    if transaction_data.get("originalData") and "{" in (
        transaction_data.get("originalData") or ""
    ):
        original_data = json.loads(transaction_data.get("originalData"))
    can_revert = can_revert_transaction(
        transaction_data.get("transactionType_id"), original_data
    )
    if not can_revert:
        raise UnprocessableParamsError(EXCEPTIONS.get("CAN_NOT_REVERT_TRANSACTION"))
    formatted_student_data = format_revert_transcation(
        original_data, request_summary.get("USER_ID")
    )
    new_original_data = format_new_original_transcation(
        prev_student_data, original_data
    )
    log_activity("Reverting Student Transaction", prev_student_data, request_summary)
    try:
        with transaction.atomic():
            student_query.update(**formatted_student_data.get("student"))
            student_uni_edu_query.update(
                **formatted_student_data.get("studentUniversityEdu")
            )
            StudentsTransactions(
                createdBy=request_summary.get("USER_ID"),
                transactionType_id=TransactionsTypeEnum.REVERT_STUDENT_DATA.value,
                uniqueId=transaction_data.get("uniqueId"),
                originalData=json.dumps(new_original_data),
                updatedData=transaction_data.get("originalData"),
            ).save()
    except DatabaseError as ex:
        handle_invalid_fk(ex)
    student_uni_data = student_uni_edu_query.values(
        "studentFaculty_id",
        "studentFaculty__name",
        "studentUniveristy_id",
        "studentUniveristy__name",
    ).first()
    return {
        "studentUniversityEdu": student_uni_data,
    }
