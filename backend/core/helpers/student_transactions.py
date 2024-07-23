import json

from django.utils import timezone

from core.models.db import Students, StudentsTransactions
from core.utils.enums import RegistrationTypeEnum, TransactionsTypeEnum


def get_student_unique_id(student_id):
    student: Students = Students.objects.filter(id=student_id).first()
    if student:
        return student.uniqueId


def create_student_transactions(
    user_id,
    unique_id,
    original_student_data,
    updated_student_data,
):
    if updated_student_data.get("student"):
        original_status = original_student_data.get("student").get("studentStatus_id")
        updated_status = updated_student_data.get("student").get("studentStatus_id")
        if updated_status and str(updated_status) != str(original_status):
            create_status_change_transaction(
                user_id, unique_id, original_status, updated_status
            )

    create_transactions(
        user_id,
        unique_id,
        original_student_data,
        updated_student_data,
        [
            # Student's basic data
            {
                "dict": "student",
                "prop": "studentName",
                "transaction_type_id": TransactionsTypeEnum.NAME_CHANGE.value,
            },
            {
                "dict": "student",
                "prop": "studentNID",
                "transaction_type_id": TransactionsTypeEnum.NID_CHANGE.value,
            },
            # Secondary education data
            {
                "dict": "studentSecondaryEdu",
                "prop": "studentTot",
                "transaction_type_id": TransactionsTypeEnum.SEC_TOTAL_CHANGE.value,
            },
            {
                "dict": "studentSecondaryEdu",
                "prop": "studentEquivTot",
                "transaction_type_id": TransactionsTypeEnum.SEC_EQV_TOTAL_CHANGE.value,
            },
            {
                "dict": "studentSecondaryEdu",
                "prop": "studentSecondaryCert_id",
                "transaction_type_id": TransactionsTypeEnum.SEC_CERT_CHANGE.value,
            },
            {
                "dict": "studentSecondaryEdu",
                "prop": "studentCertificateYear_id",
                "transaction_type_id": TransactionsTypeEnum.SEC_CERT_YEAR_CHANGE.value,
            },
            # University education data
            {
                "dict": "studentUniversityEdu",
                "prop": "studentGraduationGPA",
                "transaction_type_id": TransactionsTypeEnum.GRADUATION_GPA_CHANGE.value,
            },
            {
                "dict": "studentUniversityEdu",
                "prop": "studentGraduationGrade_id",
                "transaction_type_id": TransactionsTypeEnum.GRADUATION_GRADE_CHANGE.value,
            },
            {
                "dict": "studentUniversityEdu",
                "prop": "studentActualGraduationYear_id",
                "transaction_type_id": TransactionsTypeEnum.GRADUATION_YEAR_CHANGE.value,
            },
            {
                "dict": "studentUniversityEdu",
                "prop": "studentActualGraduationMonth_id",
                "transaction_type_id": TransactionsTypeEnum.GRADUATION_MONTH_CHANGE.value,
            },
        ],
    )


def create_transactions(user_id, unique_id, original_data, updated_data, transactions):
    for item in transactions:
        if original_data.get(item.get("dict")):
            if item.get("prop") in updated_data.get(item.get("dict")):
                original = original_data.get(item.get("dict")).get(item.get("prop"))
                updated = updated_data.get(item.get("dict")).get(item.get("prop"))
                if str(original).strip() != str(updated).strip():
                    StudentsTransactions(
                        createdBy=user_id,
                        transactionType_id=item.get("transaction_type_id"),
                        uniqueId=unique_id,
                        originalData=original,
                        updatedData=updated,
                    ).save()


def create_status_change_transaction(
    user_id, unique_id, original_status_id, new_status_id
):
    # map status id to transaction type id
    transaction_types = {1: 19, 2: 20, 3: 21, 4: 22, 5: 23, 7: 24, 8: 25}
    StudentsTransactions(
        createdBy=user_id,
        transactionType_id=transaction_types.get(new_status_id),
        uniqueId=unique_id,
        originalData=original_status_id,
        updatedData=new_status_id,
    ).save()


def create_military_education_transaction(user_id, student_id, current_data, new_data):
    unique_id = get_student_unique_id(student_id)
    original_data = None
    updated_data = None

    # Set the data
    if current_data:
        original_data = json.dumps(
            {
                "year_id": current_data.get("militaryEduYear_id"),
                "grade_id": current_data.get("militaryEduGrade_id"),
            }
        )
    if new_data:
        updated_data = json.dumps(
            {
                "year_id": new_data.get("militaryEduYear_id"),
                "grade_id": new_data.get("militaryEduGrade_id"),
            }
        )

    StudentsTransactions(
        createdBy=user_id,
        transactionType_id=TransactionsTypeEnum.MILITARY_EDU_CHANGE.value,
        uniqueId=unique_id,
        originalData=original_data,
        updatedData=updated_data,
    ).save()


def create_imposed_courses_transaction(
    user_id, unique_id, original_imposed_courses, updated_imposed_courses
):
    originalData = (
        json.dumps({"imposed_courses_ids": original_imposed_courses})
        if original_imposed_courses
        else None
    )
    updatedData = (
        json.dumps({"imposed_courses_ids": updated_imposed_courses})
        if updated_imposed_courses
        else None
    )
    StudentsTransactions(
        createdBy=user_id,
        transactionType_id=TransactionsTypeEnum.IMPOSED_COURSES_CHANGE.value,
        uniqueId=unique_id,
        originalData=originalData,
        updatedData=updatedData,
    ).save()


def create_receive_transaction(unique_id, original_data=None, updated_data=None):
    if original_data:
        original_data = json.dumps(
            {
                "tansiqid": original_data.get("tansiqid"),
                "Status_id": original_data.get("studentStatus_id"),
                "Faculty_id": original_data.get("studentFaculty_id"),
                "Univeristy_id": original_data.get("studentUniveristy_id"),
                "EnrollYear_id": original_data.get("studentEnrollYear_id"),
                "EnrollSemester_id": original_data.get("studentEnrollSemester_id"),
                "EnrollStage_id": original_data.get("studentEnrollStage_id"),
                "RegistrationType_id": original_data.get("studentRegistrationType_id"),
            }
        )

    if updated_data:
        updated_data = json.dumps(
            {
                "tansiqid": updated_data.get("tansiqid"),
                "Status_id": updated_data.get("studentStatus_id"),
                "Faculty_id": updated_data.get("studentFaculty_id"),
                "Univeristy_id": updated_data.get("studentUniveristy_id"),
                "EnrollYear_id": updated_data.get("studentEnrollYear_id"),
                "EnrollSemester_id": updated_data.get("studentEnrollSemester_id"),
                "EnrollStage_id": updated_data.get("studentEnrollStage_id"),
                "RegistrationType_id": updated_data.get("studentRegistrationType_id"),
            }
        )

    StudentsTransactions(
        createdBy=0,
        transactionType_id=TransactionsTypeEnum.ADDED_FROM_TANSIQ.value,
        uniqueId=unique_id,
        originalData=original_data,
        updatedData=updated_data,
    ).save()


def create_withdraw_transaction(unique_id, tansiqid):
    StudentsTransactions(
        createdBy=0,
        transactionType_id=TransactionsTypeEnum.WITHDRAW_BY_TANSIQ.value,
        uniqueId=unique_id,
        originalData=tansiqid,
    ).save()


def create_manual_add_student_transaction(user_id, unique_id):
    StudentsTransactions(
        createdBy=user_id,
        transactionType_id=TransactionsTypeEnum.MANUALLY_ADDED.value,
        uniqueId=unique_id,
    ).save()


def create_transfer_transaction(user_id, unique_id, original_data, updated_data):
    original_date = (
        str(original_data.get("transferDate"))
        if original_data.get("transferDate")
        else None
    )

    original_data = {
        "studentStatus_id": original_data.get("studentStatus_id"),
        "Faculty_id": original_data.get("studentFaculty_id"),
        "Univeristy_id": original_data.get("studentUniveristy_id"),
        "EnrollYear_id": original_data.get("studentEnrollYear_id"),
        "EnrollSemester_id": original_data.get("studentEnrollSemester_id"),
        "EnrollStage_id": original_data.get("studentEnrollStage_id"),
        "transferDate": original_date,
        "Level_id": original_data.get("studentLevel_id"),
        "totalEquivalentHours": original_data.get("totalEquivalentHours"),
        "RegistrationType_id": original_data.get("studentRegistrationType_id"),
    }

    updated_data = {
        "studentStatus_id": updated_data.get("studentStatus_id"),
        "Faculty_id": updated_data.get("studentFaculty_id"),
        "Univeristy_id": updated_data.get("studentUniveristy_id"),
        "EnrollYear_id": updated_data.get("studentEnrollYear_id"),
        "EnrollSemester_id": updated_data.get("studentEnrollSemester_id"),
        "EnrollStage_id": updated_data.get("studentEnrollStage_id"),
        "transferDate": updated_data.get("transferDate") or str(timezone.now().date()),
        "Level_id": updated_data.get("studentLevel_id"),
        "totalEquivalentHours": updated_data.get("totalEquivalentHours"),
        "RegistrationType_id": RegistrationTypeEnum.TRANSFER.value,
    }

    StudentsTransactions(
        createdBy=user_id,
        transactionType_id=TransactionsTypeEnum.TRANSFER_FACULTY.value,
        uniqueId=unique_id,
        originalData=json.dumps(original_data),
        updatedData=json.dumps(updated_data),
    ).save()


def create_path_shift_transaction(unique_id, original_data, updated_data):
    formatted_original_data = {
        "Status_id": original_data.get("studentStatus_id"),
        "Tot": original_data.get("studentTot"),
        "Faculty_id": original_data.get("studentFaculty_id"),
        "Univeristy_id": original_data.get("studentUniveristy_id"),
        "EnrollYear_id": original_data.get("studentEnrollYear_id"),
        "EnrollSemester_id": original_data.get("studentEnrollSemester_id"),
        "EnrollStage_id": original_data.get("studentEnrollStage_id"),
        "pathShiftDate": str(original_data.get("pathShiftDate"))
        if original_data.get("pathShiftDate")
        else None,
        "RegistrationType_id": original_data.get("studentRegistrationType_id"),
    }

    formatted_updated_data = {
        "Status_id": updated_data.get("studentStatus_id"),
        "Tot": updated_data.get("studentTot"),
        "Faculty_id": updated_data.get("studentFaculty_id"),
        "Univeristy_id": updated_data.get("studentUniveristy_id"),
        "EnrollYear_id": updated_data.get("studentEnrollYear_id"),
        "EnrollSemester_id": updated_data.get("studentEnrollSemester_id"),
        "EnrollStage_id": updated_data.get("studentEnrollStage_id"),
        "pathShiftDate": updated_data.get("pathShiftDate"),
        "RegistrationType_id": updated_data.get("studentRegistrationType_id"),
    }

    StudentsTransactions(
        createdBy=0,  # system
        transactionType_id=TransactionsTypeEnum.PATH_SHIFT.value,
        uniqueId=unique_id,
        originalData=json.dumps(formatted_original_data),
        updatedData=json.dumps(formatted_updated_data),
    ).save()
