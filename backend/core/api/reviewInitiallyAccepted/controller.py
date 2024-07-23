from django.db import DatabaseError, transaction
from django.utils import timezone

from core.helpers.general import log_activity
from core.helpers.students_validation import ValidationsRules
from core.models.db import Students, StudentsSecondaryEdu, StudentsTransactions
from core.utils.enums import StudentStatus, TransactionsTypeEnum
from core.utils.exceptions import UnprocessableParamsError
from core.utils.messages import EXCEPTIONS
from core.utils.validators import Validation


def filter_form_filters(filters: dict[str:any]):
    # Filtering only passing status
    allowed_status = []
    for item in filters["status"]:
        if item.get("id") in [
            StudentStatus.ACCEPTED.value,
            StudentStatus.FULFILLMENT.value,
            StudentStatus.REJECTED.value,
        ]:
            allowed_status.append(item)
    filters["status"] = allowed_status
    return filters


def validate_review_data(data: dict[str:any]):
    rules = ValidationsRules.review_initally_accepted(data)
    Validation.run_all_validators(rules)


def validate_prev_student_data(prev_student_data: dict[str:any]):
    for student in prev_student_data:
        print(student.get("studentStatus_id"))
        if student.get("studentStatus_id") != StudentStatus.INITIALLY_ACCEPTED.value:
            raise UnprocessableParamsError(
                EXCEPTIONS.get("STUDENT_STATUS_CHANGE_NOT_ALLOWED")
            )


def format_review_data(data: dict[str:any], user_id: str):
    updated_data = {
        "updatedAt": timezone.now(),
        "updatedBy": user_id,
    }
    formated_student = {**updated_data, "studentStatus_id": data.get("studentStatus")}
    formated_student_sec_edu = None
    if str(data.get("studentStatus")) == str(StudentStatus.FULFILLMENT.value):
        formated_student_sec_edu = {
            **updated_data,
            "studentFulfillment_id": data.get("studentFulfillment"),
        }
    return {
        "student": formated_student,
        "studentSecondaryEdu": formated_student_sec_edu,
    }


def create_student_transactions(
    data: dict[str:any], prev_student_data: dict[str, any], user_id: str
):
    # map status id to transaction type id
    transaction_types = {
        StudentStatus.ACCEPTED.value: TransactionsTypeEnum.CHANGE_TO_ACCEPTED.value,
        StudentStatus.FULFILLMENT.value: TransactionsTypeEnum.CHANGE_TO_FULFILLMENT.value,
        StudentStatus.REJECTED.value: TransactionsTypeEnum.CHANGE_TO_REJECTED.value,
    }
    student_transactions = []
    for student in prev_student_data:
        student_transactions.append(
            StudentsTransactions(
                createdBy=user_id,
                transactionType_id=transaction_types.get(data.get("studentStatus")),
                uniqueId=student.get("uniqueId"),
                originalData=student.get("studentStatus_id"),
                updatedData=data.get("studentStatus"),
            )
        )
    return student_transactions


def handle_invalid_fk(exception: Exception):
    exception_msg = str(exception)
    exception_dict = {
        "studentStatus_id": EXCEPTIONS.get("INVALID_STUDENT_STATUS_FK"),
        "studentFulfillment_id": EXCEPTIONS.get("INVALID_FULFILLMENT_FK"),
    }
    for message_key in exception_dict:
        if "foreign key constraint" in exception_msg and message_key in exception_msg:
            raise UnprocessableParamsError(exception_dict.get(message_key))
    raise UnprocessableParamsError(EXCEPTIONS.get("EDIT_STUDENT_FAIL"))


def review_student_data(data: dict[str:any], request_summary: dict[str:any]):
    validate_review_data(data)
    formated_data = format_review_data(data, request_summary.get("USER_ID"))
    student_basic_query = Students.objects.filter(id__in=data.get("studentsIds"))
    student_sec_edu_query = StudentsSecondaryEdu.objects.filter(
        student_id__in=data.get("studentsIds")
    )
    prev_student_data = list(
        student_basic_query.prefetch_related("secondary").values(
            "id",
            "createdAt",
            "createdBy",
            "updatedAt",
            "updatedBy",
            "studentStatus_id",
            "uniqueId",
            "secondary__id",
            "secondary__createdAt",
            "secondary__createdBy",
            "secondary__updatedAt",
            "secondary__updatedBy",
            "secondary__studentFulfillment_id",
        )
    )
    validate_prev_student_data(prev_student_data)
    student_transcations = create_student_transactions(
        data, prev_student_data, request_summary.get("USER_ID")
    )
    log_activity(
        "Reviewing Initially Accepted Students", prev_student_data, request_summary
    )
    try:
        with transaction.atomic():
            student_basic_query.update(**formated_data.get("student"))
            if formated_data.get("studentSecondaryEdu"):
                student_sec_edu_query.update(**formated_data.get("studentSecondaryEdu"))
            StudentsTransactions.objects.bulk_create(student_transcations)
    except DatabaseError as ex:
        handle_invalid_fk(ex)
