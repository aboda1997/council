from django.db import DatabaseError, transaction
from django.db.models import F, Subquery
from django.utils import timezone

from core.api.transferStudents.validation import get_validation_rules
from core.helpers.general import log_activity
from core.helpers.student_transactions import create_transfer_transaction
from core.helpers.students import (
    generate_student_unique_id,
    get_student_imposed_course_query,
    get_student_query,
    get_student_sec_query,
    get_student_uni_query,
)
from core.models.db import (
    Faculties,
    FacultySeatsProfiles,
    Fulfillment,
    Level,
    Semesters,
    Stages,
    StudentsAttachments,
    StudentsUniversityEdu,
    Universities,
    Years,
)
from core.utils.enums import (
    RegistrationTypeEnum,
    StudentStatus,
    UniversityIdEnum,
    UniversityTypeEnum,
)
from core.utils.exceptions import InvalidParamsError, UnprocessableParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation


def get_student(student_id: int | str):
    values_to_get = [
        "createdBy",
        "createdAt",
        "updatedAt",
        "updatedBy",
        "id",
        "studentNID",
        "studentPassport",
        "studentName",
        "studentNationality_id",
        "studentNationality__name",
        "studentStatus_id",
        "studentStatus__name",
        "uniqueId",
        "university__id",
        "university__studentExpectedGraduationYear_id",
        "university__studentExpectedGraduationYear__name",
        "university__studentExpectedGraduationMonth_id",
        "university__studentExpectedGraduationMonth__name",
        "university__studentEnrollSemester_id",
        "university__studentEnrollSemester__name",
        "university__studentEnrollStage_id",
        "university__studentEnrollStage__name",
        "university__studentEnrollYear_id",
        "university__studentEnrollYear__name",
        "university__studentFaculty_id",
        "university__studentFaculty__name",
        "university__studentUniveristy_id",
        "university__studentUniveristy__name",
        "university__studentTot",
        "university__studentCustomUniversityFaculty",
    ]
    student_query = get_student_query(student_id, "student")
    student_imposed_course = get_student_imposed_course_query(student_id)
    student_data = (
        student_query.prefetch_related("university").values(*values_to_get).first()
    )
    student_data["university__studentTot"] = round(
        float(student_data.get("university__studentTot") or "0") / 410 * 100, 2
    )
    if not student_data:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    student_imposed_courses_data = student_imposed_course.values(
        "student_id",
        "imposedCourse_id",
        "imposedCourse__name",
    )
    student_basic_data = {}
    student_uni_data = {}
    for key in student_data:
        if "university__" in key:
            student_uni_data[key.replace("university__", "")] = student_data[key]
        else:
            student_basic_data[key] = student_data[key]
    if not student_data:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    # get attachments
    attachments = (
        StudentsAttachments.objects.filter(uniqueId=student_basic_data.get("uniqueId"))
        .values("attachmentId", "filename", "mimetype")
        .all()
    )
    return {
        "student": student_basic_data,
        "studentUniversityEdu": student_uni_data,
        "studentImposedCourses": student_imposed_courses_data,
        "attachments": attachments,
    }


def get_transfer_filters(faculty_id, university_id):
    # students from external universities can be transfer to any faculty
    if university_id == str(UniversityIdEnum.EXTERNAL.value):
        return {
            "universities": Universities.objects.filter(
                typeid__in=UniversityTypeEnum.PRIVATE_NATIONAL.value
            )
            .values("id", "name")
            .order_by("name"),
            "faculties": Faculties.objects.all().values("id", "name", "univ"),
            "levels": Level.objects.all().values("id", "name"),
            "fulfillments": Fulfillment.objects.filter(typeid="2").values("id", "name"),
        }

    if not faculty_id:
        raise InvalidParamsError(EXCEPTIONS.get("MISSING_TRANSFER_FACULTY_ID"))

    faculty: Faculties = (
        Faculties.objects.filter(id=faculty_id).values("facultyname_id").first()
    )
    if not faculty:
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_TRANSFER_FACULTY_ID'))

    faculty_name_ids = get_allowed_faculties_names_ids(faculty.get("facultyname_id"))

    filters = {
        "universities": Universities.objects.filter(
            typeid__in=UniversityTypeEnum.PRIVATE_NATIONAL.value
        )
        .values("id", "name")
        .order_by("name"),
        "faculties": Faculties.objects.filter(facultyname_id__in=faculty_name_ids)
        .exclude(id=faculty_id)
        .values("id", "name", "univ"),
        "levels": Level.objects.all().values("id", "name"),
        "fulfillments": Fulfillment.objects.filter(typeid="2").values("id", "name"),
    }

    # get unique universities ids
    univ_ids = set()
    for faculty in filters.get("faculties"):
        univ_ids.add(faculty.get("univ"))

    # remove universities with no faculties
    filters["universities"] = list(
        filter(lambda univ: univ.get("id") in univ_ids, filters.get("universities"))
    )

    return filters


def get_faculty_data(faculty_id: int):
    faculty_exists = Faculties.objects.filter(id=faculty_id).exists()

    if not faculty_exists:
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_TRANSFER_FACULTY_ID"))

    transfer_data = get_transfer_availability(faculty_id)

    return {
        "can_transfer": transfer_data.get("can_transfer"),
        "allowed_transfer_count": transfer_data.get("allowed_transfer_count"),
        "transferred_students_count": transfer_data.get("transferred_students_count"),
        "available_transfer_count": transfer_data.get("available_transfer_count"),
    }


def transfer_student(
    user_id,
    student_id,
    faculty_id,
    transfer_date,
    equivalent_hours,
    transfer_level,
    fulfillment_id,
    request_summary,
):
    Validation.run_validators_set(
        get_validation_rules(
            student_id, faculty_id, transfer_date, equivalent_hours, transfer_level
        )
    )

    faculty = (
        Faculties.objects.filter(id=faculty_id)
        .values("facultyname_id", "univ_id")
        .first()
    )
    if not faculty:
        raise InvalidParamsError(EXCEPTIONS.get("INVALID_TRANSFER_FACULTY_ID"))

    student_query = get_student_query(student_id)
    student = (
        student_query.prefetch_related("university")
        .values(
            "studentNationality_id",
            "studentNID",
            "studentPassport",
            "studentStatus_id",
            "uniqueId",
            "university__studentFaculty__facultyname_id",
            "university__studentUniveristy_id",
        )
        .first()
    )
    if not student:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    if student.get("studentStatus_id") not in [
        *StudentStatus.ACCEPTANCE_STATUS.value,
        StudentStatus.WITHDRAWN.value,
    ]:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_STATUS_TRANSFER_NOT_ALLOWED"))

    # Check student national id
    # check_student_nationality(student)

    student_uni_edu_query = get_student_uni_query(student_id)
    university = student_uni_edu_query.values().first()

    current_faculty_name_id = student.get("university__studentFaculty__facultyname_id")
    in_external_university = (
        student.get("university__studentUniveristy_id")
        == UniversityIdEnum.EXTERNAL.value
    )

    # can not transfer student to current faculty or a faculty with a different `facultyname_id`
    if university.get("studentFaculty_id") == faculty_id:
        raise InvalidParamsError(EXCEPTIONS.get("NOT_ALLOWED_FACULTY_TO_TRANSFER"))
    elif not in_external_university:
        allowed_faculties_names_ids = get_allowed_faculties_names_ids(
            faculty.get("facultyname_id")
        )
        if current_faculty_name_id not in allowed_faculties_names_ids:
            raise InvalidParamsError(EXCEPTIONS.get("NOT_ALLOWED_FACULTY_TO_TRANSFER"))

    transfer_data = get_transfer_availability(faculty_id)

    if not transfer_data.get("can_transfer"):
        raise InvalidParamsError(MESSAGES.get("NO_PLACES_TO_TRANSFER"))

    student_sec_edu_query = get_student_sec_query(student_id)

    year_id, semester_id, stage_id = get_current_year_semester_stage()
    now = timezone.now()

    current_data = {
        'student': student,
        'studentUniveristyEdu': university,
    }

    updated_data = {
        "updatedAt": now,
        "updatedBy": user_id,
        "studentFaculty_id": faculty_id,
        "studentUniveristy_id": faculty.get("univ_id"),
        "studentEnrollYear_id": year_id,
        "studentEnrollSemester_id": semester_id,
        "studentEnrollStage_id": stage_id,
        "studentRegistrationType_id": RegistrationTypeEnum.TRANSFER.value,
        "studentLevel_id": transfer_level,
        "totalEquivalentHours": equivalent_hours,
        "transferDate": transfer_date or now.date(),
        "transferFulfillment_id": fulfillment_id,
    }

    updated_student_data = {
        "updatedAt": now,
        "updatedBy": user_id,
    }
    if student.get("studentStatus_id") == StudentStatus.WITHDRAWN.value:
        updated_student_data["studentStatus_id"] = StudentStatus.ACCEPTED.value

    updated_sec_edu_data = {
        "updatedAt": now,
        "updatedBy": user_id,
    }

    unique_id = student.get("uniqueId")
    if not unique_id:
        unique_id = generate_student_unique_id()
        student_query.update(uniqueId=unique_id)

    log_activity("Transfer Student", current_data, request_summary)

    try:
        with transaction.atomic():
            student_uni_edu_query.update(**updated_data)

            # update date for `student` and `secondary education`
            student_query.update(**updated_student_data)
            student_sec_edu_query.update(**updated_sec_edu_data)

            # Create transfer transaction (26)
            create_transfer_transaction(
                user_id,
                student.get("uniqueId"),
                {
                    "studentStatus_id": student.get("studentStatus_id"),
                    **university,
                },
                {
                    "studentStatus_id": updated_student_data.get(
                        "studentStatus_id", student.get("studentStatus_id")
                    ),
                    "studentFaculty_id": faculty_id,
                    "studentUniveristy_id": faculty.get("univ_id"),
                    "studentEnrollYear_id": year_id,
                    "studentEnrollSemester_id": semester_id,
                    "studentEnrollStage_id": stage_id,
                    "transferDate": transfer_date,
                    "studentLevel_id": transfer_level,
                    "totalEquivalentHours": equivalent_hours,
                },
            )

    except DatabaseError as ex:
        handle_invalid_fk(ex)


def get_transfer_availability(faculty_id):
    transfer_data = calculate_transfer_data(faculty_id)

    can_transfer = transfer_data.get("available_transfer_count") > 0

    return {
        "can_transfer": can_transfer,
        **transfer_data,
    }


def calculate_transfer_data(faculty_id):
    year_id, semester_id, stage_id = get_current_year_semester_stage()

    faculty_profile = (
        FacultySeatsProfiles.objects.filter(
            registrationType_id=RegistrationTypeEnum.TRANSFER.value,
            facultyProfile__faculty_id=faculty_id,
            facultyProfile__year_id=year_id,
            facultyProfile__semester_id=semester_id,
            facultyProfile__stage_id=stage_id,
        )
        .values("seats")
        .first()
    )

    if not faculty_profile:
        raise InvalidParamsError(EXCEPTIONS.get("NO_FACULTY_TRANSFER_PROFILE"))

    allowed_transfer_count = faculty_profile.get("seats")

    transferred_students_count = StudentsUniversityEdu.objects.filter(
        studentFaculty_id=faculty_id,
        transferDate__isnull=False,
        studentEnrollYear_id=year_id,
        studentEnrollSemester_id=semester_id,
        studentEnrollStage_id=stage_id,
        student__studentStatus_id__in=StudentStatus.ACCEPTANCE_STATUS.value,
    ).count()

    # ----- * ----- * -----

    available_transfer_count = allowed_transfer_count - transferred_students_count

    return {
        "allowed_transfer_count": allowed_transfer_count,
        "transferred_students_count": transferred_students_count,
        "available_transfer_count": available_transfer_count,
    }


def get_current_year_semester_stage():
    semester_query = Semesters.objects.filter(current=1).values("id")[:1]
    stage_query = Stages.objects.filter(current=1).values("id")[:1]
    year_query = Years.objects.filter(current=1).values("id")

    values = year_query.annotate(
        year_id=F("id"),
        semester_id=Subquery(semester_query),
        stage_id=Subquery(stage_query),
    ).first()

    return (values.get("year_id"), values.get("semester_id"), values.get("stage_id"))


def get_allowed_faculties_names_ids(target_faculty_name_id):
    allowed_faculties_names_ids = [target_faculty_name_id]

    # allow students in faculty of name id 2 to transfer to faculty of name id 12
    # الفنون التطبيقية ⇆ الفنون والتصميم
    if target_faculty_name_id in [2, 12]:
        allowed_faculties_names_ids = [2, 12]

    return allowed_faculties_names_ids


def handle_invalid_fk(exception: Exception):
    exception_msg = str(exception)
    exception_dict = {
        "studentFaculty_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="faculty", keyAr="الكلية"
        ),
        "studentUniveristy_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="university", keyAr="الجامعة"
        ),
        "studentEnrollYear_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="year", keyAr="السنة"
        ),
        "studentEnrollSemester_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="semester", keyAr="الفصل"
        ),
        "studentEnrollStage_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="stage", keyAr="المرحلة"
        ),
        "studentLevel_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="level", keyAr="المستوى"
        ),
        "transferFulfillment_id": EXCEPTIONS.get("INVALID_DB_ID").format(
            keyEn="fulfillment", keyAr="الاستيفاء"
        ),
    }
    for message_key in exception_dict:
        if "foreign key constraint" in exception_msg and message_key in exception_msg:
            raise UnprocessableParamsError(exception_dict.get(message_key))
    raise UnprocessableParamsError(EXCEPTIONS.get("EDIT_STUDENT_FAIL"))
