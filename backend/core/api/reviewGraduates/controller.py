from django.db import transaction
from django.utils import timezone

from core.helpers.general import log_activity
from core.helpers.student_transactions import (
    create_status_change_transaction,
    create_student_transactions,
)
from core.helpers.students import (
    check_student_nationality,
    get_student_imposed_course_query,
    get_student_military_edu_query,
    get_student_query,
    get_student_sec_query,
    get_student_uni_query,
)
from core.helpers.students_validation import ValidationsRules
from core.models.db import (
    Graduates,
    GraduatesImposedCourses,
    GraduatesMilitaryEdu,
    GraduatesSecondaryEdu,
    GraduatesUniversityEdu,
    Students,
    StudentsImposedCourses,
    StudentsMilitaryEdu,
    StudentsSecondaryEdu,
    StudentsUniversityEdu,
)
from core.utils.enums import GradeEnum, StudentStatus
from core.utils.exceptions import NotFoundError, UnprocessableParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation


def filter_form_filters(filters: dict[str:any]):
    # Filtering only passing grades
    allowed_grades = []
    for item in filters["grades"]:
        if item.get("id") not in GradeEnum.FAILING_GRADES.value:
            allowed_grades.append(item)
    filters["grades"] = allowed_grades
    return filters


def format_review_data(student_data: dict[str:any], user_id):
    created_data = {
        "createdAt": timezone.now(),
        "createdBy": user_id,
    }
    updated_data = {
        "updatedAt": timezone.now(),
        "updatedBy": user_id,
    }
    student_basic = {
        **updated_data,
        "studentStatus_id": StudentStatus.GRADUATE.value,
    }
    student_uni_edu = {
        **updated_data,
        "studentGraduationGPA": student_data.get("studentGraduationGPA"),
        "studentGraduationGrade_id": student_data.get("studentGraduationGrade_id"),
        "studentGraduationPercentage": student_data.get("studentGraduationPercentage"),
        "studentGraduationEquivalentHours": student_data.get(
            "studentGraduationEquivalentHours"
        ),
        "studentSpecialization": student_data.get("studentSpecialization"),
        "studentDivision": student_data.get("studentDivision"),
        "studentGraduationProjectGrade_id": student_data.get(
            "studentGraduationProjectGrade_id"
        ),
        "studentActualGraduationYear_id": student_data.get(
            "studentActualGraduationYear_id"
        ),
        "studentActualGraduationMonth_id": student_data.get(
            "studentActualGraduationMonth_id"
        ),
    }
    return {
        "student": student_basic,
        "studentSecondaryEdu": updated_data,
        "studentUniversityEdu": student_uni_edu,
        "studentMilitaryEdu": updated_data,
        "studentImposedCourses": created_data,
    }


def handle_invalid_fk(exception: Exception):
    exception_msg = str(exception)
    exception_dict = {
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


def review_student_data(
    student_id: str, student_data: dict[str:any], request_summary: dict[str:any]
):
    user_id = request_summary.get("USER_ID")
    # Formatted Form Data
    formatted_student_data = format_review_data(student_data, user_id)
    Validation.run_validators_set(
        ValidationsRules.graduation_data(
            formatted_student_data.get("studentUniversityEdu")
        )
    )
    # Queries
    student_basic_query = get_student_query(student_id)
    student_sec_edu_query = get_student_sec_query(student_id)
    student_uni_edu_query = get_student_uni_query(student_id)
    student_military_edu_query = get_student_military_edu_query(student_id)
    imposed_courses_query = get_student_imposed_course_query(student_id)

    student_basic_data = student_basic_query.values().first()
    imposed_courses_data = list(imposed_courses_query.values())

    # Validations
    if not student_basic_data:
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    if (
        student_basic_data.get("studentStatus_id")
        != StudentStatus.GRADUATION_APPLICANT.value
    ):
        raise UnprocessableParamsError(
            EXCEPTIONS.get("STUDENT_STATUS_EDIT_NOT_ALLOWED")
        )
    for course in imposed_courses_data:
        if course.get("completed") is not True:
            raise UnprocessableParamsError(EXCEPTIONS.get("STUDENT_IMPOSED_ALLOWED"))

    # Check student national id
    check_student_nationality(student_basic_data)

    # Prev Data and Logging
    prev_student_data = {
        "student": student_basic_data,
        "studentSecondaryEdu": student_sec_edu_query.values().first(),
        "studentUniveristyEdu": student_uni_edu_query.values().first(),
        "studentMilitaryEdu": student_military_edu_query.values().first(),
        "studentImposedCourses": imposed_courses_data,
    }
    log_activity("Graduating Reviewed Student", prev_student_data, request_summary)
    # Student Data
    student_basic_data = {
        **prev_student_data.get("student"),
        **formatted_student_data.get("student"),
    }
    student_sec_edu_data = {
        **prev_student_data.get("studentSecondaryEdu"),
        **formatted_student_data.get("studentSecondaryEdu"),
    }
    student_uni_edu_data = {
        **prev_student_data.get("studentUniveristyEdu"),
        **formatted_student_data.get("studentUniversityEdu"),
    }
    student_military_edu_data = prev_student_data.get("studentMilitaryEdu")
    if student_military_edu_data:
        student_military_edu_data = {
            **student_military_edu_data,
            **formatted_student_data.get("studentMilitaryEdu"),
        }
    imposed_courses_data = prev_student_data.get("studentImposedCourses")
    student_imposed_courses = []
    for entry in imposed_courses_data:
        student_imposed_courses.append(
            GraduatesImposedCourses(
                **{
                    **entry,
                    **formatted_student_data.get("studentImposedCourses"),
                }
            )
        )
    try:
        with transaction.atomic():
            Graduates(**student_basic_data).save()
            GraduatesSecondaryEdu(**student_sec_edu_data).save()
            GraduatesUniversityEdu(**student_uni_edu_data).save()
            if student_military_edu_data:
                GraduatesMilitaryEdu(**student_military_edu_data).save()
            GraduatesImposedCourses.objects.bulk_create(
                student_imposed_courses, ignore_conflicts=True
            )
            student_basic_query.delete()
            student_sec_edu_query.delete()
            student_uni_edu_query.delete()
            student_military_edu_query.delete()
            imposed_courses_query.delete()

            # create student transaction
            create_status_change_transaction(
                user_id,
                student_basic_data.get("uniqueId"),
                StudentStatus.GRADUATION_APPLICANT.value,
                StudentStatus.GRADUATE.value,
            )
            create_student_transactions(
                user_id,
                student_basic_data.get("uniqueId"),
                {"studentUniversityEdu": prev_student_data.get("studentUniveristyEdu")},
                {"studentUniversityEdu": student_uni_edu_data},
            )

        return MESSAGES.get("REVIEW_STUDENT_SUCCESS")
    except (Exception) as ex:
        handle_invalid_fk(ex)


def withdraw_graduation(student_id: str, request_summary: dict[str:any]):
    user_id = request_summary.get("USER_ID")
    # Queries
    student_basic_query = get_student_query(student_id, "graduate")
    student_sec_edu_query = get_student_sec_query(student_id, "graduate")
    student_uni_edu_query = get_student_uni_query(student_id, "graduate")
    student_military_edu_query = get_student_military_edu_query(student_id, "graduate")
    imposed_courses_query = get_student_imposed_course_query(student_id, "graduate")
    # Validations
    student_basic_data = student_basic_query.values().first()
    if not student_basic_data:
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    # Prev Data and Logging
    prev_student_data = {
        "student": student_basic_data,
        "studentSecondaryEdu": student_sec_edu_query.values().first(),
        "studentUniveristyEdu": student_uni_edu_query.values().first(),
        "studentMilitaryEdu": student_military_edu_query.values().first(),
        "studentImposedCourses": list(imposed_courses_query.values()),
    }
    log_activity("Withdrawing Student Graduation", prev_student_data, request_summary)
    # Student Data
    created_data = {
        "createdAt": timezone.now(),
        "createdBy": user_id,
    }
    updated_data = {
        "updatedAt": timezone.now(),
        "updatedBy": user_id,
    }
    student_basic_data = {
        **prev_student_data.get("student"),
        **updated_data,
        "studentStatus_id": StudentStatus.GRADUATION_APPLICANT.value,
    }
    student_sec_edu_data = {
        **prev_student_data.get("studentSecondaryEdu"),
        **updated_data,
    }
    student_uni_edu_data = {
        **prev_student_data.get("studentUniveristyEdu"),
        **updated_data,
    }
    student_military_edu_data = prev_student_data.get("studentMilitaryEdu")
    if student_military_edu_data:
        student_military_edu_data = {
            **student_military_edu_data,
            **updated_data,
        }
    imposed_courses_data = prev_student_data.get("studentImposedCourses")
    student_imposed_courses = []
    for entry in imposed_courses_data:
        student_imposed_courses.append(
            GraduatesImposedCourses(
                **{
                    **entry,
                    **created_data,
                }
            )
        )
    try:
        with transaction.atomic():
            Students(**student_basic_data).save()
            StudentsSecondaryEdu(**student_sec_edu_data).save()
            StudentsUniversityEdu(**student_uni_edu_data).save()
            if student_military_edu_data:
                StudentsMilitaryEdu(**student_military_edu_data).save()
            StudentsImposedCourses.objects.bulk_create(
                student_imposed_courses, ignore_conflicts=True
            )
            student_basic_query.delete()
            student_sec_edu_query.delete()
            student_uni_edu_query.delete()
            student_military_edu_query.delete()
            imposed_courses_query.delete()

            # create student transaction
            create_status_change_transaction(
                user_id,
                student_basic_data.get("uniqueId"),
                StudentStatus.GRADUATE.value,
                StudentStatus.GRADUATION_APPLICANT.value,
            )

        return MESSAGES.get("WITHDRAW_GRADUATE_SUCCESS")
    except (Exception):
        raise UnprocessableParamsError(EXCEPTIONS.get("EDIT_STUDENT_FAIL"))
