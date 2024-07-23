from django.db import DatabaseError, transaction
from django.utils import timezone

from core.helpers.student_transactions import (
    create_status_change_transaction,
    create_student_transactions,
)
from core.models.db import Grades, Months, Students, StudentsUniversityEdu, Years
from core.utils.enums import StudentStatus
from core.utils.messages import SERVICE_MESSSAGES
from core.utils.validators import Validation

from .validation import ValidationRules


def get_council_tables():
    return {
        "years": Years.objects.filter(tansiqid__isnull=False).values("id", "tansiqid"),
        "months": Months.objects.filter(tansiqid__isnull=False).values(
            "id", "tansiqid"
        ),
        "grades": Grades.objects.filter(tansiqid__isnull=False).values(
            "id", "tansiqid"
        ),
    }


def create_council_tables_map(council_tables: dict[str, any]):
    for table_name, table_records in council_tables.items():
        formated_dict = {}
        for record in table_records:
            formated_dict[record.get("tansiqid")] = record.get("id")
        council_tables[table_name] = formated_dict
    return council_tables


def attributes_mappings():
    return {
        "studentGraduationGrade": "grades",
        "studentGraduationProjectGrade": "grades",
        "studentActualGraduationYear": "years",
        "studentActualGraduationMonth": "months",
    }


def map_student_tansiq_ids(
    student_data: dict[str, any], council_ids_map: dict[str, any]
):
    attribute_mapping = attributes_mappings()
    for key in student_data:
        attribute_table = attribute_mapping.get(key)
        key_value = student_data.get(key)
        if attribute_table and key_value:
            attribute_table_map = council_ids_map.get(attribute_table)
            value = attribute_table_map.get(str(key_value))
            if not value:
                return {"success": False, "data": student_data}
            student_data[key] = value
    return {"success": True, "data": student_data}


def check_student_existance(tansiqid):
    target_student = (
        Students.objects.filter(tansiqid=tansiqid)
        .values("id", "studentStatus_id", "tansiqid", "uniqueId")
        .first()
    )

    if not target_student:
        return {
            "success": False,
            "code": 3,
            "message": SERVICE_MESSSAGES.get("STUDENT_NOT_FOUND"),
        }
    elif target_student and target_student.get("studentStatus_id") not in [
        StudentStatus.ACCEPTED.value
    ]:
        return {
            "success": False,
            "code": 4,
            "message": SERVICE_MESSSAGES.get("INVALID_STUDENT_ACCEPTED_STATUS"),
        }
    return {"success": True, "target_student": target_student}


def format_graduation_applicant_data(student_data: dict[str, any]):
    signature_data = {
        "updatedAt": timezone.now(),
        "updatedBy": 0,
    }
    student = {
        **signature_data,
        "studentStatus_id": StudentStatus.GRADUATION_APPLICANT.value,
    }
    student_univeristy_edu = {
        **signature_data,
        "studentGraduationGPA": student_data.get("studentGraduationGPA"),
        "studentGraduationGrade_id": student_data.get("studentGraduationGrade"),
        "studentGraduationPercentage": student_data.get("studentGraduationPercentage"),
        "studentSpecialization": student_data.get("studentSpecialization"),
        "studentDivision": student_data.get("studentDivision"),
        "studentGraduationProjectGrade_id": student_data.get(
            "studentGraduationProjectGrade"
        ),
        "studentActualGraduationYear_id": student_data.get(
            "studentActualGraduationYear"
        ),
        "studentActualGraduationMonth_id": student_data.get(
            "studentActualGraduationMonth"
        ),
    }
    return {
        "student": student,
        "studentUniversityEdu": student_univeristy_edu,
    }


def update_student_records(student, formatted_data: dict[str, dict[str, any]]):
    council_id = student.get("id")
    unique_id = student.get("uniqueId")
    status_id = student.get("uniqueId")

    try:
        with transaction.atomic():
            student_university_query = StudentsUniversityEdu.objects.filter(
                student_id=council_id
            )

            # create student transactions
            create_status_change_transaction(
                0,
                unique_id,
                status_id,
                formatted_data.get("student").get("studentStatus_id"),
            )
            create_student_transactions(
                0,
                unique_id,
                {"studentUniversityEdu": student_university_query.first().__dict__},
                {"studentUniversityEdu": formatted_data.get("studentUniversityEdu")},
            )

            Students.objects.filter(id=council_id).update(
                **formatted_data.get("student")
            )
            student_university_query.update(
                **formatted_data.get("studentUniversityEdu")
            )

        return {"success": True}
    except DatabaseError as ex:
        return {
            "success": False,
            "message": SERVICE_MESSSAGES.get("UNEXPECTED_OPERATION_ERROR")
            + " {0}".format(ex),
        }


def graduate_students(students: list[dict[str, any]]):
    council_ids_map = None
    results = []
    for student_data in students:
        student_tansiq_id = student_data.get("id")
        validation_rules = ValidationRules.student(student_data)
        validation_result = Validation.run_validators_set(
            validation_rules, supress_exceptions=True
        )
        if validation_result.get("success") is False:
            results.append(
                generate_message(
                    "fail", 2, validation_result.get("message"), id=student_tansiq_id
                )
            )
            continue

        if not council_ids_map:
            council_ids_map = create_council_tables_map(get_council_tables())

        mapped_data = map_student_tansiq_ids(student_data, council_ids_map)
        if mapped_data.get("success") is False:
            results.append(
                generate_message(
                    "fail", 2, mapped_data.get("message"), id=student_tansiq_id
                )
            )
            continue

        existance = check_student_existance(student_tansiq_id)
        if existance.get("success") is False:
            results.append(
                generate_message(
                    "fail",
                    existance.get("code"),
                    existance.get("message"),
                    id=student_tansiq_id,
                )
            )
            continue

        formatted_data = format_graduation_applicant_data(mapped_data.get("data"))
        operation_result = update_student_records(
            existance.get("target_student"), formatted_data
        )
        if operation_result.get("success") is False:
            results.append(
                generate_message(
                    "fail",
                    operation_result.get("code"),
                    operation_result.get("message"),
                    id=student_tansiq_id,
                )
            )
            continue

        results.append(
            generate_message(
                id=student_tansiq_id,
            )
        )

    return results


def check_graduate_existance(tansiqid):
    target_student = (
        Students.objects.filter(tansiqid=tansiqid)
        .prefetch_related('secondary')
        .values(
            "id",
            "studentStatus_id",
            "secondary__studentFulfillment_id",
            "tansiqid",
            "uniqueId",
        )
        .first()
    )
    if not target_student:
        return {
            "success": False,
            "code": 3,
            "message": SERVICE_MESSSAGES.get("STUDENT_NOT_FOUND"),
        }
    elif (
        target_student
        and target_student.get("studentStatus_id")
        != StudentStatus.GRADUATION_APPLICANT.value
    ):
        return {
            "success": False,
            "code": 4,
            "message": SERVICE_MESSSAGES.get("CANNOT_WITHDRAW_GRADUATION"),
        }
    return {"success": True, "target_student": target_student}


def format_withdrawal_data(fullfilment_id: str | int):
    signature_data = {
        "updatedAt": timezone.now(),
        "updatedBy": 0,
    }
    student = {
        **signature_data,
        "studentStatus_id": StudentStatus.ACCEPTED.value,
    }
    return {"student": student}


def update_widthdrawal_records(student, formatted_data: dict[str, dict[str, any]]):
    council_id = student.get("id")
    unique_id = student.get("uniqueId")
    status_id = student.get("uniqueId")

    try:
        with transaction.atomic():
            Students.objects.filter(id=council_id).update(
                **formatted_data.get("student")
            )

            # create student transactions
            create_status_change_transaction(
                0,
                unique_id,
                status_id,
                formatted_data.get("student").get("studentStatus_id"),
            )

        return {"success": True}
    except DatabaseError as ex:
        return {
            "success": False,
            "message": SERVICE_MESSSAGES.get("UNEXPECTED_OPERATION_ERROR")
            + " {0}".format(ex),
        }


def withdraw_graduates(students: list[str | int]):
    results = []
    for student_id in students:
        validation_rules = ValidationRules.database_id(
            student_id, "student", required=True
        )
        validation_result = Validation.run_validators_set(
            validation_rules, supress_exceptions=True
        )
        if validation_result.get("success") is False:
            results.append(
                generate_message(
                    "fail", 2, validation_result.get("message"), id=student_id
                )
            )
            continue

        existance = check_graduate_existance(student_id)
        if existance.get("success") is False:
            results.append(
                generate_message(
                    "fail",
                    existance.get("code"),
                    existance.get("message"),
                    id=student_id,
                )
            )
            continue

        target_student = existance.get("target_student")
        formatted_data = format_withdrawal_data(
            target_student.get("secondary__studentFulfillment_id")
        )
        operation_result = update_widthdrawal_records(target_student, formatted_data)
        if operation_result.get("success") is False:
            results.append(
                generate_message(
                    "fail",
                    operation_result.get("code"),
                    operation_result.get("message"),
                    id=student_id,
                )
            )
            continue

        results.append(
            generate_message(
                id=student_id,
            )
        )

    return results


def generate_message(
    status: str = "success",
    code: int = 1,
    message: str = SERVICE_MESSSAGES.get("STUDENT_ACCEPTED_GRADUATION"),
    **payload: dict[str, any],
):
    return {
        "status": status,
        "code": code,
        "message": message,
        **payload,
    }
