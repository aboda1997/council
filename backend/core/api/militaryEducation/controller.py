from django.db.models import Q, Subquery
from django.utils import timezone

from core.helpers.filters import get_council_filters
from core.helpers.general import get_signature, log_activity
from core.helpers.search import create_arabic_format, create_multiple_spaces_format
from core.helpers.student_transactions import create_military_education_transaction
from core.helpers.students import get_student_military_edu_query, get_student_query
from core.models.db import Grades, Students, StudentsMilitaryEdu, Years
from core.utils.enums import GenderEnum, GradeEnum, MilitaryStatusType, StudentStatus
from core.utils.exceptions import InvalidParamsError, NotFoundError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation, Validators


def get_form_filters(student_id):
    student_query = get_student_query(student_id)
    student_data = (
        student_query.prefetch_related("university")
        .values("id", "university__studentEnrollYear__code")
        .first()
    )
    if not student_data or not student_data.get("id"):
        NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    enroll_year_code = int(student_data.get("university__studentEnrollYear__code"))
    filters = get_council_filters(
        [
            "years",
            "months",
            "acedemicGrades",
        ]
    )
    # Filtering years greater or equal to enrollement year
    allowed_years = []
    for item in filters["years"]:
        current_code = int(item.get("code"))
        if current_code >= enroll_year_code:
            allowed_years.append(item)
    filters["years"] = allowed_years
    # Filtering only passing grades
    allowed_grades = []
    for item in filters["acedemicGrades"]:
        if item.get("id") not in GradeEnum.FAILING_GRADES.value:
            allowed_grades.append(item)
    filters["acedemicGrades"] = allowed_grades
    return filters


def get_military_data(student_id):
    military_query = get_student_military_edu_query(student_id)
    military_data = military_query.values(
        'createdBy',
        'createdAt',
        'updatedAt',
        'updatedBy',
        'id',
        'student_id',
        'student__studentName',
        'militaryEduYear_id',
        'militaryEduYear__name',
        'militaryEduMonth_id',
        'militaryEduMonth__name',
        'militaryEduGrade_id',
        'militaryEduGrade__name',
    ).first()
    if not military_data:
        raise InvalidParamsError(EXCEPTIONS.get('MILITARY_DOES_NOT_EXIST'))
    signature = get_signature(military_data)
    return {
        'studentMilitaryEdu': military_data,
        'signature': signature,
    }


def format_military_data(
    student_id: str, military_data: dict[str:any], user_id: str, is_edit: bool
):
    formated_military_data = {
        'student_id': student_id,
        'militaryEduYear_id': military_data.get('militaryEduYear_id'),
        'militaryEduMonth_id': military_data.get('militaryEduMonth_id'),
        'militaryEduGrade_id': military_data.get('militaryEduGrade_id'),
    }
    if is_edit:
        formated_military_data['updatedAt'] = timezone.now()
        formated_military_data['updatedBy'] = user_id
    else:
        formated_military_data['createdBy'] = user_id
    return formated_military_data


def validate_military_data(military_data: dict[str:any]):
    validation_rules = [
        [
            Validators.required(),
            military_data.get("militaryEduGrade_id"),
            EXCEPTIONS.get('MISSING_MILITARY_GRADE'),
        ],
        [
            Validators.isInteger(),
            military_data.get("militaryEduGrade_id"),
            EXCEPTIONS.get('INVALID_GRADE_FK'),
        ],
        [
            Validators.isNotIn(GradeEnum.FAILING_GRADES.value),
            military_data.get("militaryEduGrade_id"),
            EXCEPTIONS.get('INVALID_FAIL_MILITARY_GRADE'),
        ],
        [
            Validators.required(),
            military_data.get("militaryEduYear_id"),
            EXCEPTIONS.get('MISSING_MILITARY_YEAR'),
        ],
        [
            Validators.isInteger(),
            military_data.get("militaryEduYear_id"),
            EXCEPTIONS.get('INVALID_YEAR_FK'),
        ],
        [
            Validators.required(),
            military_data.get("militaryEduMonth_id"),
            EXCEPTIONS.get('MISSING_MILITARY_MONTH'),
        ],
        [
            Validators.isInteger(),
            military_data.get("militaryEduMonth_id"),
            EXCEPTIONS.get('INVALID_MONTH_FK'),
        ],
    ]
    Validation.run_validators_set(validation_rules)


def validate_military_data_fk(military_data: dict[str:any]):
    student_query = get_student_query(military_data.get('student_id'))
    grades_query = Grades.objects.filter(
        id=military_data.get('militaryEduGrade_id'), typeid=1
    ).values('id')[:1]
    year_query = Years.objects.filter(
        id=military_data.get('militaryEduYear_id')
    ).values('code')[:1]

    # Gets all data in a single query
    fk_data = (
        student_query.prefetch_related("university")
        .values(
            'studentNID',
            'studentGender_id',
            'studentStatus_id',
            'university__studentEnrollYear__code',
        )
        .annotate(
            grades_id=Subquery(grades_query),
            year_code=Subquery(year_query),
        )
        .first()
    )
    if not fk_data:
        raise NotFoundError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    if not fk_data.get('studentGender_id') == GenderEnum.MALE.value:
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_MILITARY_GENDER'))
    if not fk_data.get('studentNID'):
        raise InvalidParamsError(EXCEPTIONS.get('MISSING_NID_ADD_VIA_INQUIRE'))
    if fk_data.get('studentStatus_id') == StudentStatus.INITIALLY_ACCEPTED.value:
        raise InvalidParamsError(EXCEPTIONS.get('STUDENT_STATUS_EDIT_NOT_ALLOWED'))
    if not fk_data.get('grades_id'):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_GRADE_FK'))
    if not fk_data.get('year_code'):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_YEAR_FK'))
    if not int(fk_data.get('year_code')) >= int(
        fk_data.get('university__studentEnrollYear__code')
    ):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_LTE_MILITARY_YEAR'))


def add_military_data(student_id: str, military_data: dict[str:any], user_id: str):
    military_query = get_student_military_edu_query(student_id)
    if military_query.exists():
        raise InvalidParamsError(MESSAGES.get('ADD_NEW_MILITARY_EXIST'))
    military_data = format_military_data(student_id, military_data, user_id, False)
    validate_military_data(military_data)
    validate_military_data_fk(military_data)
    try:
        StudentsMilitaryEdu.objects.create(**military_data)
        create_military_education_transaction(user_id, student_id, None, military_data)
        return MESSAGES.get('ADD_NEW_MILITARY_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('ADD_OPERATION_FAIL'))


def edit_military_data(
    student_id: str, military_data: dict[str:any], request_summary: dict[str:any]
):
    user_id = request_summary.get("USER_ID")
    military_query = get_student_military_edu_query(student_id)
    prev_military_data = military_query.values().first()
    if not military_query.exists():
        raise InvalidParamsError(EXCEPTIONS.get('MILITARY_DOES_NOT_EXIST'))
    military_data = format_military_data(student_id, military_data, user_id, True)
    validate_military_data(military_data)
    validate_military_data_fk(military_data)
    log_activity(
        "Editing Student Military Education", prev_military_data, request_summary
    )
    try:
        military_query.update(**military_data)
        create_military_education_transaction(
            user_id, student_id, prev_military_data, military_data
        )
        return MESSAGES.get('EDIT_MILITARY_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('EDIT_OPERATION_FAIL'))


def delete_military_data(student_id: str, user_id: str, request_summary: dict[str:any]):
    military_query = get_student_military_edu_query(student_id)
    prev_military_data = military_query.values().first()
    if not military_query.exists():
        raise InvalidParamsError(EXCEPTIONS.get('MILITARY_DOES_NOT_EXIST'))
    log_activity(
        "Deleting Student Military Education", prev_military_data, request_summary
    )
    try:
        military_query.delete()
        create_military_education_transaction(
            user_id, student_id, prev_military_data, None
        )
        return MESSAGES.get('DELETE_MILITARY_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('DELETE_OPERATION_FAIL'))


def get_military_list(search_data: dict[str, any], page: str, per_page: str):
    filter = {
        'studentGender': GenderEnum.MALE.value,
    }
    exclude = {
        'studentStatus_id': StudentStatus.INITIALLY_ACCEPTED.value,
    }
    offset = int(page) * int(per_page)
    limit = int(offset) + int(per_page)
    list_query = []
    validation_rules = []

    if search_data.get('studentName'):
        student_name_field = " ".join(search_data.get('studentName').split())

        name_parts = student_name_field.split()
        validation_rules.append(
            [
                Validators.isLettersOnly(),
                student_name_field,
                EXCEPTIONS.get('INVALID_STUDENT_NAME_SYMBOLS'),
            ]
        )
        validation_rules.append(
            [
                Validators.maxLength(100),
                student_name_field,
                EXCEPTIONS.get('INVALID_STUDENT_NAME_LENGTH'),
            ]
        )
        validation_rules.append(
            [
                Validators.minLength(2),
                name_parts,
                EXCEPTIONS.get('INVALID_STUDENT_NAMES_COUNT'),
            ]
        )
        for part in name_parts:
            validation_rules.append(
                [
                    Validators.minLength(2),
                    part,
                    EXCEPTIONS.get('INVALID_STUDENT_NAME_SIZE'),
                ]
            )

        search_regex = create_multiple_spaces_format(student_name_field)
        search_regex = create_arabic_format(search_regex)
        filter['studentName__iregex'] = search_regex

    if search_data.get('nationalID'):
        validation_rules.append(
            [
                Validators.equalLength(14),
                search_data.get('nationalID'),
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        validation_rules.append(
            [
                Validators.isNationalID(),
                search_data.get('nationalID'),
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        filter['studentNID'] = search_data.get('nationalID')

    if search_data.get('university'):
        filter['university__studentUniveristy'] = search_data.get('university')

    if search_data.get('university') and search_data.get('faculty'):
        filter['university__studentFaculty'] = search_data.get('faculty')

    if search_data.get('militaryStatusType') == MilitaryStatusType.PERFORMED.value:
        filter['military__isnull'] = False
    elif (
        search_data.get('militaryStatusType') == MilitaryStatusType.NOT_PERFORMED.value
    ):
        filter['military__isnull'] = True

    Validation.run_validators_set(validation_rules)

    list_query = (
        Students.objects.filter(Q(studentNationality="1") | Q(studentNID__isnull=False))
        .filter(**filter)
        .exclude(**exclude)
    )
    final_list_query = list(
        list_query.values(
            'id',
            'studentNID',
            'studentName',
            'university__studentUniveristy__name',
            'university__studentFaculty__name',
            'secondary__studentSecondaryCert__name',
            'secondary__studentCertificateYear__name',
            'university__studentTot',
            'military__militaryEduYear_id',
        ).order_by('studentName')[offset:limit]
    )

    total_records = list_query.count()
    students_list = final_list_query
    return {'studentsList': students_list, 'totalRecords': total_records}
