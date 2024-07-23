from django.db.models import Subquery, Value

from core.helpers.search import create_arabic_format, create_multiple_spaces_format
from core.models.gsdb import (
    ControlList,
    Governorates,
    LanguagesList,
    NationalityList,
    SchoolCodeList,
    SchoolTypeList,
    StageNew,
    StudentGenderList,
    StudentReligionList,
    StudentsBranchList,
)
from core.utils.exceptions import InvalidParamsError, NotFoundError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.validators import Validation, Validators


def get_cd_student_query(national_id: str, seat_no: str):
    student_query = ""
    validation_rules = []
    if seat_no:
        validation_rules.append(
            [
                Validators.maxLength(9),
                seat_no,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ]
        )
        validation_rules.append(
            [
                Validators.isInteger(),
                seat_no,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ]
        )
        student_query = StageNew.objects.filter(seating_no__exact=seat_no)
    elif national_id:
        validation_rules.append(
            [
                Validators.equalLength(14),
                national_id,
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        validation_rules.append(
            [
                Validators.isNationalID(),
                national_id,
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        student_query = StageNew.objects.filter(national_no__exact=national_id)
    else:
        raise InvalidParamsError(EXCEPTIONS.get('INPUT_ID_VALUE'))
    Validation.run_validators_set(validation_rules)
    return student_query


def get_cd_student(year_code: str, national_id: str, seat_no: str):
    db_name = "gs_" + year_code
    student_query = get_cd_student_query(national_id, seat_no)
    student_data = (
        student_query.values(
            'branch_code_new',
            'gender_id',
            'religion_id',
            'school_type_id',
            'school_code',
            'control_code',
            'city_code',
            'nationality',
            'lang_1',
            'lang_2',
        )
        .using(db_name)
        .first()
    )
    if not student_data:
        raise InvalidParamsError(EXCEPTIONS.get('STUDENT_DOES_NOT_EXIST'))
    # Addtional Student Data
    branch_query = StudentsBranchList.objects.filter(
        branch_code__exact=student_data.get('branch_code_new', '')
    ).values('branch_name')[:1]
    gender_query = StudentGenderList.objects.filter(
        gender_code__exact=student_data.get('gender_id', '')
    ).values('gender_name')[:1]
    religion_query = StudentReligionList.objects.filter(
        religion_code__exact=student_data.get('religion_id', '')
    ).values('religion_name')[:1]
    school_type_query = SchoolTypeList.objects.filter(
        school_type_code__exact=student_data.get('school_type_id', '')
    ).values('school_type_name')[:1]
    school_code_query = SchoolCodeList.objects.filter(
        school_code__exact=student_data.get('school_code', '')
    ).values('school_name')[:1]
    control_query = ControlList.objects.filter(
        control_code__exact=student_data.get('control_code', '')
    ).values('control_name')[:1]
    governorate_query = Governorates.objects.filter(
        governorate_code__exact=student_data.get('city_code', '')
    ).values('governorate_name')[:1]
    nationality_query = NationalityList.objects.filter(
        nationality_code__exact=student_data.get('nationality', '')
    ).values('nationality_name')[:1]
    first_lang_query = LanguagesList.objects.filter(
        lang_code__exact=student_data.get('lang_1', '')
    ).values('lang_name')[:1]
    second_lang_query = LanguagesList.objects.filter(
        lang_code__exact=student_data.get('lang_2', '')
    ).values('lang_name')[:1]

    student_data = (
        student_query.values()
        .annotate(
            branch_name=Subquery(branch_query),
            gender_name=Subquery(gender_query),
            religion_name=Subquery(religion_query),
            school_type_name=Subquery(school_type_query),
            school_code_name=Subquery(school_code_query),
            control_name=Subquery(control_query),
            governorate_name=Subquery(governorate_query),
            nationality_name=Subquery(nationality_query),
            first_lang_name=Subquery(first_lang_query),
            second_lang_name=Subquery(second_lang_query),
            cert_year=Value(year_code),
        )
        .using(db_name)
        .first()
    )
    return {'student': student_data}


def validate_cd_student(
    year_code: str,
    student_data: dict[str, any],
    prev_student_data: dict[str, any] = None,
):
    db_name = "gs_" + year_code
    validation_rules = [
        [
            Validators.required(),
            student_data.get("arabic_name", None),
            MESSAGES.get("REQUIRED_STUDENT_NAME"),
        ],
        [
            Validators.isLettersOnly(),
            student_data.get("arabic_name"),
            EXCEPTIONS.get('INVALID_STUDENT_NAME_SYMBOLS'),
        ],
        [
            Validators.maxLength(100),
            student_data.get("arabic_name"),
            EXCEPTIONS.get('INVALID_STUDENT_NAME_LENGTH'),
        ],
        [
            Validators.minLength(2),
            student_data.get("arabic_name"),
            EXCEPTIONS.get('INVALID_STUDENT_NAMES_COUNT'),
        ],
        [
            Validators.required(),
            student_data.get("national_no"),
            EXCEPTIONS.get('MISSING_NATIONAL_ID'),
        ],
        [
            Validators.equalLength(14),
            student_data.get("national_no"),
            EXCEPTIONS.get('INVALID_NATIONAL_ID'),
        ],
        [
            Validators.isNationalID(),
            student_data.get("national_no"),
            EXCEPTIONS.get('INVALID_NATIONAL_ID'),
        ],
        [
            Validators.required(),
            student_data.get("seating_no"),
            EXCEPTIONS.get('MISSING_SEATING_NUMBER'),
        ],
        [
            Validators.maxLength(9),
            student_data.get("seating_no"),
            EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
        ],
        [
            Validators.isInteger(),
            student_data.get("seating_no"),
            EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
        ],
        [
            Validators.maxLength(100),
            student_data.get("school_name"),
            EXCEPTIONS.get('INVALID_SCHOOL_NAME_LENGTH'),
        ],
        [
            Validators.maxLength(200),
            student_data.get("birth_palace"),
            EXCEPTIONS.get('INVALID_BIRTH_PLACE_LENGTH'),
        ],
        [
            Validators.required(),
            student_data.get("branch_code_new"),
            EXCEPTIONS.get('REQUIRED_STUDENT_BRANCH'),
        ],
        [
            Validators.isInteger(),
            student_data.get("branch_code_new"),
            EXCEPTIONS.get('INVALID_STUDENT_BRANCH'),
        ],
        [
            Validators.isInteger(),
            student_data.get("branch_code_new"),
            EXCEPTIONS.get('INVALID_STUDENT_BRANCH'),
        ],
        [
            Validators.required(),
            student_data.get("tanseq_number"),
            EXCEPTIONS.get('MISSING_TANSIQ_NUMBER'),
        ],
        [
            Validators.maxLength(9),
            student_data.get("tanseq_number"),
            EXCEPTIONS.get('INVALID_TANSIQ_NUMBER'),
        ],
        [
            Validators.isInteger(),
            student_data.get("tanseq_number"),
            EXCEPTIONS.get('INVALID_TANSIQ_NUMBER'),
        ],
        [
            Validators.required(),
            student_data.get("total_degree"),
            EXCEPTIONS.get('MISSING_TOTAL_GRADE'),
        ],
        [
            Validators.isFloat(),
            student_data.get("total_degree"),
            EXCEPTIONS.get('INVALID_TOTAL_GRADE'),
        ],
        [
            Validators.isInteger(),
            student_data.get("lang_1"),
            EXCEPTIONS.get('INVALID_LANG_SECOND'),
        ],
        [
            Validators.isInteger(),
            student_data.get("lang_2"),
            EXCEPTIONS.get('INVALID_LANG_SECOND'),
        ],
        [
            Validators.notEqual(student_data.get("lang_1")),
            student_data.get("lang_2"),
            EXCEPTIONS.get('INVALID_EQUAL_LANG_SECOND'),
        ],
        [
            Validators.maxLength(75),
            student_data.get("bar_code"),
            EXCEPTIONS.get('INVALID_BARCODE_LENGTH'),
        ],
        [
            Validators.maxLength(250),
            student_data.get("address"),
            EXCEPTIONS.get('INVALID_ADDRESS_LENGTH'),
        ],
        [
            Validators.maxLength(100),
            student_data.get("police_station"),
            EXCEPTIONS.get('INVALID_POLICE_LENGTH'),
        ],
    ]
    name_parts = (student_data.get("arabic_name") or "").split()
    student_data["arabic_name"] = " ".join(name_parts)
    validation_rules.insert(
        1,
        [
            Validators.minLength(4),
            name_parts,
            EXCEPTIONS.get('INVALID_STUDENT_FULL_NAME'),
        ],
    )
    for part in name_parts:
        validation_rules.insert(
            4,
            [
                Validators.minLength(2),
                part,
                EXCEPTIONS.get('INVALID_STUDENT_NAME_SIZE'),
            ],
        )
    degree_arr = [
        'arabic_deg',
        'lang_1_deg',
        'lang_2_deg',
        'pure_math_deg',
        'history_deg',
        'geography_deg',
        'philosophy_deg',
        'psychology_deg',
        'chemistry_deg',
        'biology_deg',
        'geology_deg',
        'applied_math_deg',
        'physics_deg',
        'religious_education_deg',
        'national_education_deg',
        'economics_deg',
    ]
    for key in degree_arr:
        validation_rules.append(
            [
                Validators.isFloat(),
                student_data.get(key),
                EXCEPTIONS.get('INVALID_SUBJECT_GRADE'),
            ],
        )
    Validation.run_validators_set(validation_rules)

    # Database Checks
    seating_no = None
    national_no = None
    tansiq_number = None
    bar_code = None
    if prev_student_data:
        if prev_student_data.get("seating_no") != student_data.get("seating_no"):
            seating_no = student_data.get("seating_no")
        if prev_student_data.get("national_no") != student_data.get("national_no"):
            national_no = student_data.get("national_no")
        if prev_student_data.get("tansiq_number") != student_data.get("tansiq_number"):
            tansiq_number = student_data.get("tansiq_number")
        if prev_student_data.get("bar_code") != student_data.get("bar_code"):
            bar_code = student_data.get("bar_code")
    else:
        seating_no = student_data.get("seating_no")
        national_no = student_data.get("national_no")
        tansiq_number = student_data.get("tansiq_number")
        bar_code = student_data.get("bar_code")

    if seating_no:
        check_seating_number = (
            StageNew.objects.using(db_name).filter(seating_no__exact=seating_no).count()
        )
        if check_seating_number > 0:
            raise InvalidParamsError(EXCEPTIONS.get('CHECK_SEAT_NUMBER_FAIL'))
    if national_no:
        check_national_id = (
            StageNew.objects.using(db_name)
            .filter(national_no__exact=national_no)
            .count()
        )
        if check_national_id > 0:
            raise InvalidParamsError(EXCEPTIONS.get('CHECK_NATIONAL_ID_FAIL'))
    if tansiq_number:
        check_tansiq_number = (
            StageNew.objects.using(db_name)
            .filter(tanseq_number__exact=tansiq_number)
            .count()
        )
        if check_tansiq_number > 0:
            raise InvalidParamsError(EXCEPTIONS.get('CHECK_TANSIQ_NUMBER_FAIL'))
    if bar_code:
        check_bar_code = (
            StageNew.objects.using(db_name).filter(bar_code__exact=bar_code).count()
        )
        if check_bar_code > 0:
            raise InvalidParamsError(EXCEPTIONS.get('CHECK_BARCODE_FAIL'))
    return True


def format_cd_student(year_code, student_data: dict[str, any]):
    computed_total_degrees = 0
    undefined_degrees = 0
    degree_arr = [
        'arabic_deg',
        'lang_1_deg',
        'lang_2_deg',
        'pure_math_deg',
        'history_deg',
        'geography_deg',
        'philosophy_deg',
        'psychology_deg',
        'chemistry_deg',
        'biology_deg',
        'geology_deg',
        'applied_math_deg',
        'physics_deg',
    ]
    for key in degree_arr:
        degree = student_data.get(key)
        if degree and degree >= 0:
            computed_total_degrees += degree
        else:
            undefined_degrees += 1
    if undefined_degrees != len(degree_arr):
        student_data['total_degree'] = computed_total_degrees
    student_data['religious_education_deg'] = (
        -abs(student_data.get("religious_education_deg"))
        if (student_data.get("religious_education_deg"))
        else None
    )
    student_data['national_education_deg'] = (
        -abs(student_data.get("national_education_deg"))
        if (student_data.get("national_education_deg"))
        else None
    )
    student_data['economics_deg'] = (
        -abs(student_data.get("economics_deg"))
        if (student_data.get("economics_deg"))
        else None
    )
    formated_student = {
        'arabic_name': student_data.get("arabic_name", None),
        'seating_no': student_data.get("seating_no", None),
        'school_name': student_data.get("school_name", None),
        'dept_name': student_data.get("dept_name", None),
        'city_name': student_data.get("city_name", None),
        'gender_id': student_data.get("gender_id", None),
        'religion_id': student_data.get("religion_id", None),
        'national_no': student_data.get("national_no", None),
        'school_type_id': student_data.get("school_type_id", None),
        'branch_code_new': student_data.get("branch_code_new", None),
        'control_code': student_data.get("control_code", None),
        'year': student_data.get("year", None),
        'month': student_data.get("month", None),
        'day': student_data.get("day", None),
        'moderia': student_data.get("moderia", None),
        'nationality': student_data.get("nationality", None),
        'lang_1': student_data.get("lang_1", None),
        'lang_2': student_data.get("lang_2", None),
        'dept_code': student_data.get("dept_code", None),
        'police_code': student_data.get("police_code", None),
        'address': student_data.get("address", None),
        'police_station': student_data.get("police_station", None),
        'city_code': student_data.get("city_code", None),
        'birth_palace': student_data.get("birth_palace", None),
        'school_code': student_data.get("school_code", None),
        'tanseq_number': student_data.get("tanseq_number", None),
        'bar_code': student_data.get("bar_code", None),
        'arabic_deg': student_data.get("arabic_deg", None),
        'lang_1_deg': student_data.get("lang_1_deg", None),
        'lang_2_deg': student_data.get("lang_2_deg", None),
        'pure_math_deg': student_data.get("pure_math_deg", None),
        'history_deg': student_data.get("history_deg", None),
        'geography_deg': student_data.get("geography_deg", None),
        'philosophy_deg': student_data.get("philosophy_deg", None),
        'psychology_deg': student_data.get("psychology_deg", None),
        'chemistry_deg': student_data.get("chemistry_deg", None),
        'biology_deg': student_data.get("biology_deg", None),
        'geology_deg': student_data.get("geology_deg", None),
        'applied_math_deg': student_data.get("applied_math_deg", None),
        'physics_deg': student_data.get("physics_deg", None),
        'total_degree': student_data.get("total_degree", None),
        'religious_education_deg': student_data.get("religious_education_deg", None),
        'national_education_deg': student_data.get("national_education_deg", None),
        'economics_deg': student_data.get("economics_deg", None),
        'no_of_fail': student_data.get("no_of_fail", None),
    }
    return formated_student


def add_cd_student(year_code: str, student_data: dict[str, any]):
    db_name = "gs_" + year_code
    student_data = format_cd_student(year_code, student_data)
    validate_cd_student(year_code, student_data)
    try:
        StageNew.objects.using(db_name).create(**student_data)
        return MESSAGES.get('ADD_STUDENT_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('ADD_STUDENT_FAIL'))


def edit_cd_student(
    year_code: str, national_id: str, seat_no: str, student_data: dict[str, any]
):
    db_name = "gs_" + year_code
    student_query = get_cd_student_query(national_id, seat_no)
    prev_student_data = get_cd_student(year_code, national_id, seat_no)['student']
    student_data = format_cd_student(year_code, student_data)
    validate_cd_student(year_code, student_data, prev_student_data)
    # TODO log student data before editing
    try:
        student_query.using(db_name).update(**student_data)
        return MESSAGES.get('EDIT_STUDENT_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('EDIT_STUDENT_FAIL'))


def delete_cd_student(year_code: str, national_id: str, seat_no: str):
    db_name = "gs_" + year_code
    student_query = get_cd_student_query(national_id, seat_no)
    if not student_query.exists():
        raise InvalidParamsError(EXCEPTIONS.get('STUDENT_DOES_NOT_EXIST'))
    try:
        student_query.using(db_name).delete()
        return MESSAGES.get('DELETE_STUDENT_SUCCESS')
    except (Exception):
        raise InvalidParamsError(EXCEPTIONS.get('DELETE_STUDENT_FAIL'))


def get_cd_students_list(
    year_code: str, search_type: str, search_field: str, page: int, per_page: int
):
    offset = int(page) * int(per_page)
    limit = int(offset) + int(per_page)
    list_query = []
    validation_rules = []
    db_name = "gs_" + year_code
    search_field = " ".join(search_field.split())
    if search_type == "studentName":
        name_parts = search_field.split()
        validation_rules.append(
            [
                Validators.isLettersOnly(),
                search_field,
                EXCEPTIONS.get('INVALID_STUDENT_NAME_SYMBOLS'),
            ]
        )
        validation_rules.append(
            [
                Validators.maxLength(100),
                search_field,
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
        Validation.run_validators_set(validation_rules)
        search_regex = create_multiple_spaces_format(search_field)
        search_regex = create_arabic_format(search_regex)
        list_query = StageNew.objects.filter(arabic_name__iregex=search_regex)
    elif search_type == "nationalID":
        validation_rules.append(
            [
                Validators.equalLength(14),
                search_field,
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        validation_rules.append(
            [
                Validators.isNationalID(),
                search_field,
                EXCEPTIONS.get('INVALID_NATIONAL_ID'),
            ]
        )
        Validation.run_validators_set(validation_rules)
        list_query = StageNew.objects.filter(national_no__exact=search_field)
    elif search_type == "seatNumber":
        validation_rules.append(
            [
                Validators.maxLength(9),
                search_field,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ]
        )
        validation_rules.append(
            [
                Validators.isInteger(),
                search_field,
                EXCEPTIONS.get('INVALID_SEATING_NUMBER'),
            ]
        )
        Validation.run_validators_set(validation_rules)
        list_query = StageNew.objects.filter(seating_no__exact=search_field)
    else:
        raise InvalidParamsError(EXCEPTIONS.get('INPUT_TYPE_INVALID'))
    # TODO: Remove try and catch and check if the db_name exists
    try:
        students_list = list(
            list_query.values('seating_no', 'arabic_name', 'city_name', 'national_no')
            .annotate(cert_year=Value(year_code))
            .order_by('arabic_name')
            .using(db_name)[offset:limit]
        )
        total_records = list_query.using(db_name).count()
    except Exception as exception:
        if f"The connection '{db_name}' doesn't exist." == str(exception):
            raise NotFoundError(EXCEPTIONS.get('MISSING_GS_CD'))
    return {'studentsList': students_list, 'totalRecords': total_records}
