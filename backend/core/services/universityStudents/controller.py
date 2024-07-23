import re

from core.models.db import Students
from core.utils.enums import StudentStatus
from core.utils.validators import Validation

from .validation import ValidationRules


def get_students_list(request_data: dict[str, any], page: str, per_page: str):
    request_data["page"] = page
    request_data["perPage"] = per_page
    validation_rules = ValidationRules.studentFilters(request_data)
    validation_result = Validation.run_validators_set(
        validation_rules, supress_exceptions=True
    )
    if validation_result.get("message"):
        return {
            "status_code": 422,
            "status": "fail",
            "message": validation_result.get("message"),
        }

    filter = {
        "studentStatus_id__in": [
            StudentStatus.ACCEPTED.value,
            StudentStatus.FULFILLMENT.value,
            StudentStatus.GRADUATION_APPLICANT.value,
        ]
    }
    offset = int(page) * int(per_page)
    limit = int(offset) + int(per_page)

    if request_data.get("facultyId"):
        filter["university__studentFaculty__tansiqid__iregex"] = (
            r"\|*\b" + re.escape(request_data.get("facultyId")) + r"\b\|*"
        )
    if request_data.get("univeristyId"):
        filter["university__studentUniveristy__tansiqid"] = request_data.get(
            "univeristyId"
        )

    list_query = (
        Students.objects.prefetch_related("university", "secondary")
        .filter(**filter)
        .order_by("studentName")
    )
    student_count = list_query.count()
    students_data = list(
        list_query.values(
            "id",
            "tansiqid",
            "uniqueId",
            "studentName",
            "studentNID",
            "studentStatus__id",
            "studentStatus__name",
            "university__studentTot",
            "secondary__studentSecondaryCert__tansiqid",
            "secondary__studentSecondaryCert__name",
            "university__studentFaculty__tansiqid",
            "university__studentFaculty__name",
            "university__studentUniveristy__tansiqid",
            "university__studentUniveristy__name",
        )[offset:limit]
    )
    students_data = formalize_students_list(students_data)
    return {"studentCount": student_count, "studentsData": students_data}


def formalize_students_list(students_data: list[dict[str, any]]):
    index = 0
    for student in students_data:
        students_data[index] = {
            "id": student.get("tansiqid"),
            "councilId": student.get("id"),
            "uniqueId": student.get("uniqueId"),
            "studentName": student.get("studentName"),
            "studentNID": student.get("studentNID"),
            "studentStatusId": student.get("studentStatus__id"),
            "studentStatusName": student.get("studentStatus__name"),
            "studentSecondaryDegree": student.get("university__studentTot"),
            "studentSecondaryPercentage": round(
                float(student.get("university__studentTot") or "0") / 410 * 100, 2
            ),
            "secondaryCertId": student.get("secondary__studentSecondaryCert__tansiqid"),
            "secondaryCertName": student.get("secondary__studentSecondaryCert__name"),
            "facultyId": student.get("university__studentFaculty__tansiqid"),
            "facultyName": student.get("university__studentFaculty__name"),
            "universityId": student.get("university__studentUniveristy__tansiqid"),
            "universityName": student.get("university__studentUniveristy__name"),
        }
        index += 1
    return students_data
