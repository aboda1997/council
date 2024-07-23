from core.models.db import Students
from core.utils.exceptions import InvalidParamsError


def get_report_data(search_data: dict[str, any]):
    if search_data.get("university") is None:
        raise InvalidParamsError("University name should not be Empty")
    filters = {}
    if search_data.get('studentStatus'):
        if isinstance(search_data.get('studentStatus'), list):
            filters['studentStatus__in'] = search_data.get('studentStatus')
        else:
            filters['studentStatus'] = search_data.get('studentStatus')
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
            filters[filter_mapping.get(key)] = search_data.get(key)
    res = []
    all_data = list(
        Students.objects.prefetch_related("secondary", "university")
        .filter(**filters)
        .values(
            "secondary__studentSecondaryCert__name",
            "secondary__studentCertificateYear__name",
            "secondary__studentTot",
            "studentNID",
            "studentName",
            "studentStatus__name",
            "studentNationality__name",
            "notes",
            "university__studentRegistrationType__name",
            "university__studentUniveristy__name",
            "university__studentFaculty__name",
            "university__studentFaculty__univ",
            "university__studentEnrollYear",
        )
        .order_by(
            "university__studentFaculty__name", "university__student__studentName"
        )
    )
    for data in all_data:
        total = data.get("secondary__studentTot")
        if total is None:
            percentage = None
        else:
            percentage = str(round(float(total) * 100 / 410, 2)) + "%"
        res.append(
            {
                "university": "university__studentUniveristy__name",
                "nationalID": data.get("studentNID"),
                "studentStatus": data.get("studentStatus__name"),
                "registrationType": data.get(
                    "university__studentRegistrationType__name"
                ),
                "faculty": data.get("university__studentFaculty__name"),
                "name": data.get("studentName"),
                "certificate": data.get("secondary__studentSecondaryCert__name"),
                "nationality": data.get("studentNationality__name"),
                "certificateYear": data.get("secondary__studentCertificateYear__name"),
                "total": total,
                "percentage": percentage,
                "notes": data.get("notes"),
            }
        )
    return {
        "columns": [
            "faculty",
            "name",
            "nationalID",
            "studentStatus",
            "registrationType",
            "certificate",
            "certificateYear",
            "nationality",
            "total",
            "percentage",
            "notes",
        ],
        "reportData": res,
    }
