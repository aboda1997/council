import json
import re
from base64 import b64encode
from datetime import datetime
from os import urandom

from django.db.models import Subquery, Value

from core.helpers.filters import get_council_filters
from core.helpers.general import get_signature, run_sql_command
from core.helpers.search import create_arabic_format, create_multiple_spaces_format
from core.helpers.students_validation import ValidationsRules
from core.models.db import (
    Faculties,
    Graduates,
    GraduatesImposedCourses,
    GraduatesMilitaryEdu,
    GraduatesSecondaryEdu,
    GraduatesUniversityEdu,
    Semesters,
    Stages,
    Students,
    StudentsAttachments,
    StudentsImposedCourses,
    StudentsMilitaryEdu,
    StudentsSecondaryEdu,
    StudentsTransactions,
    StudentsUniversityEdu,
    Universities,
    Years,
)
from core.utils.enums import (
    CertificateEnum,
    CountryEnum,
    RegistrationTypeEnum,
    StudentStatus,
    TransactionsTypeEnum,
    UniversityIdEnum,
)
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS
from core.utils.validators import Validation, Validators


def generate_student_unique_id(creation_date=datetime.now()):
    if isinstance(creation_date, str):
        creation_date = datetime.fromisoformat(creation_date)
    timestamp = str(int(creation_date.timestamp()))[2:]
    uid = re.sub(r"[/+]", "0", b64encode(urandom(9)).decode("UTF-8")).upper()
    return (
        timestamp[:5] + "-" + timestamp[5:] + uid[:2] + "-" + uid[2:7] + "-" + uid[7:]
    )


def get_student_query(student_id: str, student_type: str = "student"):
    Validation.run_validators_set(
        ValidationsRules.database_id(student_id, "student", "طالب", True)
    )
    if student_type == "student":
        return Students.objects.filter(id=student_id)
    elif student_type == "graduate":
        return Graduates.objects.filter(id=student_id)
    raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))


def get_student_sec_query(student_id: str, student_type: str = "student"):
    Validation.run_validators_set(
        ValidationsRules.database_id(student_id, "student", "طالب", True)
    )
    if student_type == "student":
        return StudentsSecondaryEdu.objects.filter(student_id=student_id)
    elif student_type == "graduate":
        return GraduatesSecondaryEdu.objects.filter(student_id=student_id)
    raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))


def get_student_uni_query(student_id: str, student_type: str = "student"):
    Validation.run_validators_set(
        ValidationsRules.database_id(student_id, "student", "طالب", True)
    )
    if student_type == "student":
        return StudentsUniversityEdu.objects.filter(student_id=student_id)
    elif student_type == "graduate":
        return GraduatesUniversityEdu.objects.filter(student_id=student_id)
    raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))


def get_student_imposed_course_query(student_id: str, student_type: str = "student"):
    Validation.run_validators_set(
        ValidationsRules.database_id(student_id, "student", "طالب", True)
    )
    if student_type == "student":
        return StudentsImposedCourses.objects.filter(student_id=student_id)
    elif student_type == "graduate":
        return GraduatesImposedCourses.objects.filter(student_id=student_id)
    raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))


def get_student_military_edu_query(student_id: str, student_type: str = "student"):
    Validation.run_validators_set(
        ValidationsRules.database_id(
            student_id,
            "student military eduation",
            "بيان الطالب للتربية العسكرية",
            True,
        )
    )
    if student_type == "student":
        return StudentsMilitaryEdu.objects.filter(student_id=student_id)
    elif student_type == "graduate":
        return GraduatesMilitaryEdu.objects.filter(student_id=student_id)
    raise InvalidParamsError(EXCEPTIONS.get("INVALID_STUDENT_TYPE"))


def get_student(
    student_id: int | str,
    student_type: str = "student",
    show_graduation_data=False,
    show_prev_transfer_data=False,
):
    values_to_get = [
        "createdBy",
        "createdAt",
        "updatedAt",
        "updatedBy",
        "id",
        "studentNID",
        "studentPassport",
        "studentName",
        "studentPhone",
        "studentMail",
        "studentAddress",
        "studentBirthDate",
        "studentGender_id",
        "studentGender__name",
        "studentAddressPlaceGov_id",
        "studentAddressPlaceGov__name",
        "studentBirthPlaceGov_id",
        "studentBirthPlaceGov__name",
        "studentNationality_id",
        "studentNationality__name",
        "studentReligion_id",
        "studentReligion__name",
        "studentStatus_id",
        "studentStatus__name",
        "uniqueId",
        "notes",
        "secondary__id",
        "secondary__studentTot",
        "secondary__studentEquivTot",
        "secondary__studentSportDegree",
        "secondary__studentComplainGain",
        "secondary__studentCertificateYear_id",
        "secondary__studentCertificateYear__name",
        "secondary__studentSecondaryCert_id",
        "secondary__studentSecondaryCert__name",
        "secondary__studentStudyGroup_id",
        "secondary__studentStudyGroup__name",
        "secondary__studentFulfillment_id",
        "secondary__studentFulfillment__name",
        "secondary__studentSeatNumber",
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
        "university__studentRegistrationType_id",
        "university__studentRegistrationType__name",
        "university__studentCustomUniversityFaculty",
        "university__transferDate",
        "military__id",
        "military__militaryEduYear__name",
        "military__militaryEduMonth__name",
        "military__militaryEduGrade__name",
    ]
    if show_graduation_data:
        values_to_get = [
            *values_to_get,
            "university__studentGraduationGPA",
            "university__studentGraduationGrade_id",
            "university__studentGraduationGrade__name",
            "university__studentGraduationPercentage",
            "university__studentGraduationEquivalentHours",
            "university__studentSpecialization",
            "university__studentDivision",
            "university__studentGraduationProjectGrade_id",
            "university__studentGraduationProjectGrade__name",
            "university__studentActualGraduationYear_id",
            "university__studentActualGraduationYear__name",
            "university__studentActualGraduationMonth_id",
            "university__studentActualGraduationMonth__name",
        ]
    student_query = get_student_query(student_id, student_type)
    student_imposed_course = get_student_imposed_course_query(student_id, student_type)
    student_data = (
        student_query.prefetch_related("university", "secondary", "military")
        .values(*values_to_get)
        .first()
    )
    if not student_data:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    student_basic_data = {}
    student_sec_data = {}
    student_uni_data = {}
    student_military_data = {}
    for key in student_data:
        if "secondary__" in key:
            student_sec_data[key.replace("secondary__", "")] = student_data[key]
        elif "university__" in key:
            student_uni_data[key.replace("university__", "")] = student_data[key]
        elif "military__" in key:
            student_military_data[key.replace("military__", "")] = student_data[key]
        else:
            student_basic_data[key] = student_data[key]
    if not student_data:
        raise InvalidParamsError(EXCEPTIONS.get("STUDENT_DOES_NOT_EXIST"))
    student_imposed_courses_data = student_imposed_course.values(
        "student_id",
        "imposedCourse_id",
        "imposedCourse__name",
        "completed",
    )
    if show_prev_transfer_data:
        student_uni_data = get_student_transfer_data(
            student_basic_data, student_uni_data, student_type
        )
    if student_basic_data.get("studentStatus_id") == StudentStatus.WITHDRAWN.value:
        student_basic_data["withdrawalDate"] = get_widthdrawal_date(student_basic_data)
    signature = get_signature(student_data)
    # get attachments
    attachments = (
        StudentsAttachments.objects.filter(uniqueId=student_basic_data.get("uniqueId"))
        .values("attachmentId", "filename", "mimetype")
        .all()
    )
    return {
        "student": student_basic_data,
        "studentSecondaryEdu": student_sec_data,
        "studentUniversityEdu": student_uni_data,
        "studentMilitaryEdu": student_military_data,
        "studentImposedCourses": student_imposed_courses_data,
        "attachments": attachments,
        "signature": signature,
    }


def get_student_transfer_data(
    student_basic_data, student_uni_data, student_type: str = "student"
):
    if not (
        student_uni_data.get("transferDate")
        or student_uni_data.get("studentRegistrationType_id")
        == RegistrationTypeEnum.TRANSFER.value
    ):
        return student_uni_data
    transction_data = (
        StudentsTransactions.objects.filter(
            uniqueId=student_basic_data.get("uniqueId"),
            transactionType_id=TransactionsTypeEnum.TRANSFER_FACULTY.value,
        )
        .order_by("createdAt")
        .values()
        .last()
    ) or {}
    original_data = (
        json.loads(transction_data.get("originalData"))
        if transction_data.get("originalData")
        else {}
    )
    subqueries = {}
    prev_faculty_id = original_data.get("Faculty_id") or original_data.get(
        "studentFaculty_id"
    )
    if prev_faculty_id:
        subqueries["studentPrevFaculty_id"] = Value(prev_faculty_id)
        subqueries["studentPrevFaculty__name"] = Subquery(
            Faculties.objects.filter(id=prev_faculty_id).values("name")[:1]
        )
    prev_university_id = original_data.get("Univeristy_id") or original_data.get(
        "studentUniveristy_id"
    )
    if prev_university_id:
        subqueries["studentPrevUniveristy_id"] = Value(prev_university_id)
        subqueries["studentPrevUniveristy__name"] = Subquery(
            Universities.objects.filter(id=prev_university_id).values("name")[:1]
        )
    if original_data.get("EnrollYear_id"):
        subqueries["studentPrevEnrollYear_id"] = Value(
            original_data.get("EnrollYear_id")
        )
        subqueries["studentPrevEnrollYear__name"] = Subquery(
            Years.objects.filter(id=original_data.get("EnrollYear_id")).values("name")[
                :1
            ]
        )
    if original_data.get("EnrollSemester_id"):
        subqueries["studentPrevEnrollSemester_id"] = Value(
            original_data.get("EnrollSemester_id")
        )
        subqueries["studentPrevEnrollSemester__name"] = Subquery(
            Semesters.objects.filter(id=original_data.get("EnrollSemester_id")).values(
                "name"
            )[:1]
        )
    if original_data.get("EnrollStage_id"):
        subqueries["studentPrevEnrollStage_id"] = Value(
            original_data.get("EnrollStage_id")
        )
        subqueries["studentPrevEnrollStage__name"] = Subquery(
            Stages.objects.filter(id=original_data.get("EnrollStage_id")).values(
                "name"
            )[:1]
        )
    student_uni_query = get_student_uni_query(
        student_basic_data.get("id"), student_type
    )
    transfer_data = (
        student_uni_query.values(
            "studentLevel_id",
            "studentLevel__name",
            "totalEquivalentHours",
            "transferDate",
            "transferFulfillment_id",
            "transferFulfillment__name",
            "studentCustomUniversityFaculty",
        )
        .annotate(**subqueries)
        .first()
    )
    student_uni_data["studentPrevCustomUniversityFaculty"] = original_data.get(
        "CustomUniversityFaculty"
    ) or transfer_data.get("studentCustomUniversityFaculty")
    return {**student_uni_data, **transfer_data}


def get_widthdrawal_date(student_basic_data: dict[str:any]):
    transction_data = (
        StudentsTransactions.objects.filter(
            uniqueId=student_basic_data.get("uniqueId"),
            transactionType_id=TransactionsTypeEnum.CHANGE_TO_WITHDRAWN.value,
        )
        .order_by("createdAt")
        .values()
        .last()
    ) or {}
    withdrawal_date = transction_data.get("createdAt") or student_basic_data.get(
        "createdAt"
    )
    withdrawal_date = str(withdrawal_date.strftime("%Y-%m-%d"))
    return withdrawal_date


def get_student_transactions_data(uniqueId: str):
    sql_params = [uniqueId]
    sql_query = """
    SELECT
        studentstransactions.id AS id,
        studentstransactions.createdAt AS createdAt,
        studentstransactions.createdBy AS createdBy_Id,
        IFNULL( users.fullname, "مستخدم غير معروف|Unknown User" ) AS createdBy,
        studentstransactions.transactionType_id AS transactionType_id,
        transactionstype.name AS transactionType__name,
        studentstransactions.originalData AS originalData,
        studentstransactions.updatedData AS updatedData
    FROM
        studentstransactions
        LEFT JOIN users ON studentstransactions.createdBy = users.id
        INNER JOIN transactionstype ON studentstransactions.transactionType_id = transactionstype.id
    WHERE
        studentstransactions.uniqueId = %s
    ORDER BY
        studentstransactions.createdAt
    """
    return run_sql_command(sql_query, sql_params, 2)


def find_item_name_filter(id, filters):
    if not id:
        return None
    if isinstance(id, list):
        filter_name = [item.get("name") for item in filters if item.get('id') in id]
        return filter_name
    filter_name = [item.get("name") for item in filters if item.get('id') == id]
    if len(filter_name) == 0:
        return None
    return filter_name[0]


def get_transcation_change(original_key, updated_key, filters):
    original = find_item_name_filter(original_key, filters)
    updated = find_item_name_filter(updated_key, filters)
    if not original and not updated:
        return None
    return {
        "from": original or "فارغ|Empty",
        "to": updated or "فارغ|Empty",
    }


def can_revert_transaction(
    transcation_type: int, transaction_original_data: dict[str, any]
):
    if not isinstance(transaction_original_data, dict):
        return False
    # Must have the fields, each array must have a value,
    # Example (studentUniveristy_id or Univeristy_id) AND (studentFaculty_id or Faculty_id)
    required_mappings = {
        TransactionsTypeEnum.TRANSFER_FACULTY.value: [
            ["studentUniveristy_id", "Univeristy_id"],
            ["studentFaculty_id", "Faculty_id"],
            ["studentEnrollYear_id", "EnrollYear_id"],
            ["studentEnrollSemester_id", "EnrollSemester_id"],
            ["studentEnrollStage_id", "EnrollStage_id"],
            ["RegistrationType_id"],
        ],
        TransactionsTypeEnum.PATH_SHIFT.value: [
            ["studentUniveristy_id", "Univeristy_id"],
            ["studentFaculty_id", "Faculty_id"],
            ["studentEnrollYear_id", "EnrollYear_id"],
            ["studentEnrollSemester_id", "EnrollSemester_id"],
            ["studentEnrollStage_id", "EnrollStage_id"],
            ["RegistrationType_id"],
        ],
        TransactionsTypeEnum.WITHDRAW_BY_OLD_COUNCIL.value: [
            ["studentUniveristy_id", "Univeristy_id"],
            ["studentFaculty_id", "Faculty_id"],
            ["studentEnrollYear_id", "EnrollYear_id"],
            ["studentEnrollSemester_id", "EnrollSemester_id"],
            ["studentEnrollStage_id", "EnrollStage_id"],
            ["RegistrationType_id"],
        ],
        TransactionsTypeEnum.DATA_FROM_OLD_SYSTEM.value: [
            ["studentUniveristy_id", "Univeristy_id"],
            ["studentFaculty_id", "Faculty_id"],
            ["studentEnrollYear_id", "EnrollYear_id"],
            ["studentEnrollSemester_id", "EnrollSemester_id"],
            ["studentEnrollStage_id", "EnrollStage_id"],
            ["RegistrationType_id"],
        ],
        TransactionsTypeEnum.REVERT_STUDENT_DATA.value: [
            ["studentUniveristy_id", "Univeristy_id"],
            ["studentFaculty_id", "Faculty_id"],
            ["studentEnrollYear_id", "EnrollYear_id"],
            ["studentEnrollSemester_id", "EnrollSemester_id"],
            ["studentEnrollStage_id", "EnrollStage_id"],
            ["RegistrationType_id"],
        ],
    }
    fields_arrays = required_mappings.get(transcation_type)
    if not fields_arrays:
        return False
    can_revert = False
    for array in fields_arrays:
        for field in array:
            can_revert = bool(transaction_original_data.get(field))
            if transaction_original_data.get(field):
                break
        if not can_revert:
            break
    return can_revert


def formalize_student_transactions(
    type_filter_map: dict[str, dict[str, any]],
    filters: list[dict[str, any]],
    transactions_data: list[dict[str, any]],
):
    formalized_transactions_data = []
    for transaction in transactions_data:
        # Filters out some of the data that will be sent
        formalized_transaction = {
            "id": transaction.get("id"),
            "createdAt": transaction.get("createdAt"),
            "createdBy": transaction.get("createdBy"),
            "transactionType_id": transaction.get("transactionType_id"),
            "transactionType__name": transaction.get("transactionType__name"),
        }

        # Sets system users, if created by id 0
        if transaction.get("createdBy_Id") == 0:
            formalized_transaction["createdBy"] = "النظام|System"

        # Sets icon depending on transaction type (Creation, Modification/Edit, Transfer/Path Shift)
        transactionType = int(transaction.get("transactionType_id"))
        if transactionType in [
            TransactionsTypeEnum.ADDED_FROM_TANSIQ.value,
            TransactionsTypeEnum.MANUALLY_ADDED.value,
        ]:
            formalized_transaction["icon"] = "plus"
        elif transactionType in [
            TransactionsTypeEnum.TRANSFER_FACULTY.value,
            TransactionsTypeEnum.PATH_SHIFT.value,
        ]:
            formalized_transaction["icon"] = "sync"
        else:
            formalized_transaction["icon"] = "pencil"

        # Deserializes json string
        if transaction.get("originalData") and "{" in (
            transaction.get("originalData") or ""
        ):
            transaction["originalData"] = json.loads(transaction.get("originalData"))
        if transaction.get("updatedData") and "{" in (
            transaction.get("updatedData") or ""
        ):
            transaction["updatedData"] = json.loads(transaction.get("updatedData"))
        original_data = transaction.get("originalData")
        updated_data = transaction.get("updatedData")
        transactionType = int(transaction.get("transactionType_id"))
        formalized_transaction["transactionChanges"] = []
        formalized_transaction["canRevert"] = can_revert_transaction(
            transactionType, original_data
        )
        if transactionType == TransactionsTypeEnum.TRANSFER_FACULTY.value:
            transfer_date = updated_data.get("transferDate")
            if transfer_date:
                formalized_transaction["transactionChanges"].append(
                    {
                        "keyword": "transferDate",
                        "value": transfer_date,
                    }
                )
        elif transactionType == TransactionsTypeEnum.PATH_SHIFT.value:
            transfer_date = transaction.get("createdAt").strftime("%Y-%m-%d")
            formalized_transaction["transactionChanges"].append(
                {
                    "keyword": "transferDate",
                    "value": transfer_date,
                }
            )
        elif transactionType == TransactionsTypeEnum.WITHDRAW_BY_OLD_COUNCIL.value:
            withdraw_date = original_data.get("withdrawDate")
            withdraw_notes = original_data.get("withdrawNotes")
            if withdraw_date:
                formalized_transaction["transactionChanges"].append(
                    {
                        "keyword": "withdrawalDate",
                        "value": withdraw_date,
                    }
                )
            if withdraw_notes:
                formalized_transaction["transactionChanges"].append(
                    {
                        "keyword": "notes",
                        "value": withdraw_notes,
                    }
                )
        if transactionType in [
            TransactionsTypeEnum.NAME_CHANGE.value,
            TransactionsTypeEnum.NID_CHANGE.value,
            TransactionsTypeEnum.SEC_TOTAL_CHANGE.value,
            TransactionsTypeEnum.SEC_EQV_TOTAL_CHANGE.value,
            TransactionsTypeEnum.GRADUATION_GPA_CHANGE.value,
        ]:
            formalized_transaction["transactionChanges"].append(
                {
                    "from": original_data or "فارغ|Empty",
                    "to": updated_data or "فارغ|Empty",
                }
            )
        elif transactionType in type_filter_map.keys():
            if type_filter_map.get(transactionType).get("default"):
                filter_key = type_filter_map.get(transactionType).get("default")
                formalized_transaction["transactionChanges"].append(
                    get_transcation_change(
                        original_data, updated_data, filters.get(filter_key)
                    )
                )
            else:
                for key in type_filter_map.get(transactionType):
                    filter_key = type_filter_map.get(transactionType).get(key)
                    original_key = None
                    updated_key = None
                    if original_data:
                        original_key = original_data.get(key)
                    if updated_data:
                        updated_key = updated_data.get(key)
                    transaction_change = None
                    if filter_key == "none":
                        transaction_change = {
                            "from": original_key or "فارغ|Empty",
                            "to": updated_key or "فارغ|Empty",
                        }
                    else:
                        transaction_change = get_transcation_change(
                            original_key, updated_key, filters.get(filter_key)
                        )
                    if transaction_change:
                        formalized_transaction["transactionChanges"].append(
                            transaction_change
                        )

        formalized_transactions_data.append(formalized_transaction)
    return formalized_transactions_data


def get_student_history(student_id: str, student_type: str = "student"):
    student_query = get_student_query(student_id, student_type)
    student_data = student_query.values("id", "studentName", "uniqueId").first()
    transactions_data = get_student_transactions_data(student_data.get("uniqueId"))
    type_filter_map = {
        TransactionsTypeEnum.SEC_CERT_CHANGE.value: {
            "default": "certificates",
        },
        TransactionsTypeEnum.SEC_CERT_YEAR_CHANGE.value: {"default": "years"},
        TransactionsTypeEnum.GRADUATION_YEAR_CHANGE.value: {"default": "years"},
        TransactionsTypeEnum.GRADUATION_MONTH_CHANGE.value: {"default": "months"},
        TransactionsTypeEnum.GRADUATION_GRADE_CHANGE.value: {"default": "grades"},
        TransactionsTypeEnum.IMPOSED_COURSES_CHANGE.value: {
            "imposed_courses_ids": "imposedCourses"
        },
        TransactionsTypeEnum.MILITARY_EDU_CHANGE.value: {
            "year_id": "years",
            "grade_id": "grades",
        },
        TransactionsTypeEnum.TRANSFER_FACULTY.value: {
            "studentUniveristy_id": "universities",
            "Univeristy_id": "universities",
            "studentFaculty_id": "faculties",
            "Faculty_id": "faculties",
            "studentEnrollYear_id": "years",
            "EnrollYear_id": "years",
            "studentEnrollSemester_id": "semesters",
            "EnrollSemester_id": "semesters",
            "studentEnrollStage_id": "stages",
            "EnrollStage_id": "stages",
            "RegistrationType_id": "allRegistrationTypes",
        },
        TransactionsTypeEnum.PATH_SHIFT.value: {
            "Univeristy_id": "universities",
            "Faculty_id": "faculties",
            "EnrollYear_id": "years",
            "EnrollSemester_id": "semesters",
            "EnrollStage_id": "stages",
            "RegistrationType_id": "allRegistrationTypes",
        },
        TransactionsTypeEnum.WITHDRAW_BY_OLD_COUNCIL.value: {
            "Univeristy_id": "universities",
            "Faculty_id": "faculties",
            "EnrollYear_id": "years",
            "EnrollSemester_id": "semesters",
            "EnrollStage_id": "stages",
            "RegistrationType_id": "allRegistrationTypes",
        },
        TransactionsTypeEnum.DATA_FROM_OLD_SYSTEM.value: {
            "Univeristy_id": "universities",
            "Faculty_id": "faculties",
            "EnrollYear_id": "years",
            "EnrollSemester_id": "semesters",
            "EnrollStage_id": "stages",
            "RegistrationType_id": "allRegistrationTypes",
        },
        TransactionsTypeEnum.REVERT_STUDENT_DATA.value: {
            "Univeristy_id": "universities",
            "Faculty_id": "faculties",
            "EnrollYear_id": "years",
            "EnrollSemester_id": "semesters",
            "EnrollStage_id": "stages",
            "RegistrationType_id": "allRegistrationTypes",
        },
    }
    filters_names = set()
    for transaction in transactions_data:
        # Adjusts the filters names required to be queried
        transactionType = int(transaction.get("transactionType_id"))
        if type_filter_map.get(transactionType):
            filters_names.update(type_filter_map.get(transactionType).values())
    filters = get_council_filters(list(filters_names))
    transactions_data = formalize_student_transactions(
        type_filter_map,
        filters,
        transactions_data,
    )
    return {
        "student": student_data,
        "transactions": transactions_data,
    }


def get_students_list(search_data: dict[str, any], page: str, per_page: str):
    filter = {}
    offset = int(page) * int(per_page)
    limit = int(offset) + int(per_page)
    list_query = []
    validation_rules = []

    if search_data.get('studentName'):
        validation_rules = [
            *validation_rules,
            *ValidationsRules.student_name(search_data.get('studentName'), 2),
        ]
        student_name_field = create_multiple_spaces_format(
            search_data.get('studentName')
        )
        search_regex = create_arabic_format(student_name_field)
        filter['studentName__iregex'] = search_regex

    if search_data.get('nationalID'):
        validation_rules = [
            *validation_rules,
            *ValidationsRules.national_id(search_data.get('nationalID')),
        ]
        filter['studentNID'] = search_data.get('nationalID')

    if search_data.get('seatNumber') and str(search_data.get('certificate')) == str(
        CertificateEnum.EGYPTIAN_GENERAL_SECONADARY.value
    ):
        validation_rules = [
            *validation_rules,
            *ValidationsRules.seat_number(search_data.get('seatNumber')),
        ]
        filter['secondary__studentSeatNumber'] = search_data.get('seatNumber')

    if search_data.get('passport') and str(search_data.get('region')) != str(
        CountryEnum.EGYPT.value
    ):
        validation_rules = [
            *validation_rules,
            *ValidationsRules.passport(search_data.get('passport')),
        ]
        filter['studentPassport'] = search_data.get('passport')

    if search_data.get('studentStatus'):
        if isinstance(search_data.get('studentStatus'), list):
            filter['studentStatus__in'] = search_data.get('studentStatus')
        else:
            filter['studentStatus'] = search_data.get('studentStatus')

    filter_mapping = {
        'region': 'studentNationality',
        'universityYear': 'university__studentEnrollYear',
        'semester': 'university__studentEnrollSemester',
        'stage': 'university__studentEnrollStage',
        'certificate': 'secondary__studentSecondaryCert',
        'gsYear': 'secondary__studentCertificateYear',
        'fulfillment': 'secondary__studentFulfillment_id',
        'university': 'university__studentUniveristy',
        'faculty': 'university__studentFaculty',
        'registrationType': 'university__studentRegistrationType_id',
    }
    for key in filter_mapping:
        if search_data.get(key):
            filter[filter_mapping.get(key)] = search_data.get(key)

    Validation.run_validators_set(validation_rules)

    if (
        not search_data.get("selectedStudentType")
        or search_data.get("selectedStudentType") == "student"
    ):
        list_query = (
            Students.objects.prefetch_related("university", "secondary")
            .filter(**filter)
            .order_by("studentName")
        )
    elif search_data.get("selectedStudentType") == "graduate":
        list_query = (
            Graduates.objects.prefetch_related("university", "secondary")
            .filter(**filter)
            .order_by("studentName")
        )

    final_list_query = list(
        list_query.values(
            'id',
            'studentName',
            'studentStatus_id',
            'studentStatus__name',
            'studentNationality__name',
            'secondary__studentSecondaryCert__name',
            'secondary__studentCertificateYear__name',
            'university__studentUniveristy__id',
            'university__studentUniveristy__name',
            'university__studentFaculty__name',
            'university__studentTot',
            'university__studentGraduationGPA',
        )[offset:limit]
    )

    for each_student in final_list_query:
        # If the university is external, sets the fac name as external as well
        if (
            each_student.get('university__studentUniveristy__id')
            == UniversityIdEnum.EXTERNAL.value
        ):
            each_student['university__studentFaculty__name'] = each_student.get(
                'university__studentUniveristy__name'
            )
        del each_student['university__studentUniveristy__id']
        each_student['university__studentTot'] = round(
            float(each_student.get('university__studentTot') or "0") / 410 * 100, 2
        )

    total_records = list_query.count()
    students_list = final_list_query
    return {'studentsList': students_list, 'totalRecords': total_records}


def check_student_nationality(student):
    validation_rules = []
    if (
        not student.get("studentNationality_id")
        or student.get("studentNationality_id") == CountryEnum.EGYPT.value
    ):
        national_id = student.get("studentNID")
        validation_rules = [
            [
                Validators.required(),
                national_id,
                EXCEPTIONS.get("MISSING_NID_ADD_VIA_INQUIRE"),
            ],
            [
                Validators.equalLength(14),
                national_id,
                EXCEPTIONS.get("MISSING_NID_ADD_VIA_INQUIRE"),
            ],
            [
                Validators.isNationalID(),
                national_id,
                EXCEPTIONS.get("MISSING_NID_ADD_VIA_INQUIRE"),
            ],
        ]
    else:
        passport = student.get("studentPassport")
        validation_rules = [
            [
                Validators.maxLength(20),
                passport,
                EXCEPTIONS.get('MISSING_PASSPORT_ADD_VIA_INQUIRE'),
            ]
        ]
    Validation.run_validators_set(validation_rules)
