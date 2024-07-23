from core.models.db import (
    Certificates,
    Faculties,
    FacultyName,
    Fulfillment,
    Gender,
    Grades,
    ImposedCourses,
    Level,
    Months,
    Regions,
    RegistrationType,
    Religion,
    Sectors,
    Semesters,
    Stages,
    Status,
    StudyGroups,
    Universities,
    Years,
)
from core.models.gsdb import (
    ControlList,
    EducationalAdministrations,
    Governorates,
    LanguagesList,
    NationalityList,
    SchoolCodeList,
    SchoolTypeList,
    StudentGenderList,
    StudentReligionList,
    StudentsBranchList,
)
from core.utils.enums import UniversityTypeEnum


def get_council_filters(selected_filters=["*"]):
    query_dict = {
        "years": Years.objects.all()
        .values("id", "name", "code", "current")
        .order_by("-code"),
        "genders": Gender.objects.all().values("id", "name", "code"),
        "certificates": Certificates.objects.all().values("id", "name", "code"),
        "stages": Stages.objects.all().values("id", "name", "code", "current"),
        "semesters": Semesters.objects.all().values("id", "name", "code", "current"),
        "regions": Regions.objects.all().values(
            "id", "name", "type", "typeid", "parent", "gscdid"
        ),
        "countries": Regions.objects.filter(typeid="1").values(
            "id", "name", "type", "typeid", "parent", "gscdid"
        ),
        "governorates": Regions.objects.filter(typeid="2").values(
            "id", "name", "type", "typeid", "parent", "gscdid"
        ),
        "adminstrations": Regions.objects.filter(typeid="3").values(
            "id", "name", "type", "typeid", "parent", "gscdid"
        ),
        "universities": Universities.objects.filter(
            typeid__in=[
                *UniversityTypeEnum.PRIVATE_NATIONAL.value,
                UniversityTypeEnum.EXTERNAL.value,
            ]
        ).values("id", "name", "gov", "typeid", "type"),
        "studyGroups": StudyGroups.objects.all().values("id", "name", "code"),
        "sectors": Sectors.objects.all().values("id", "name"),
        "faculties": Faculties.objects.all().values(
            "id", "name", "sector", "facultyname", "studygroup", "univ", "facode"
        ),
        "facultiesNames": FacultyName.objects.all().values("id", "name"),
        "status": Status.objects.all().values("id", "name", "code"),
        "religions": Religion.objects.all().values("id", "name", "code"),
        "months": Months.objects.all().values("id", "name", "code"),
        "fulfillments": Fulfillment.objects.all().values(
            "id", "name", "typeid", "type"
        ),
        "imposedCourses": ImposedCourses.objects.all().values("id", "name", "code"),
        "grades": Grades.objects.filter().values(
            "id", "name", "code", "typeid", "type"
        ),
        "acedemicGrades": Grades.objects.filter(typeid="1").values(
            "id", "name", "code", "typeid", "type"
        ),
        "creditGrades": Grades.objects.filter(typeid="2").values(
            "id", "name", "code", "typeid", "type"
        ),
        "registrationTypes": RegistrationType.objects.filter(active=True).values(
            "id", "name", "active"
        ),
        "allRegistrationTypes": RegistrationType.objects.all().values(
            "id", "name", "active"
        ),
        "levels": Level.objects.all().values("id", "name"),
    }
    filters_data = {}
    if "*" in selected_filters:
        for key in query_dict:
            filters_data[key] = list(query_dict[key])
    else:
        for key in selected_filters:
            query = query_dict.get(key)
            if query:
                filters_data[key] = list(query)
    return filters_data


def get_gs_filters(year_code="2021", selected_filters=["*"]):
    db_name = "gs_" + year_code
    query_dict = {
        "governorates": Governorates.objects.using(db_name).all().values(),
        "educationalAdministrations": EducationalAdministrations.objects.using(db_name)
        .all()
        .values(),
        "studentsBranchList": StudentsBranchList.objects.using(db_name).all().values(),
        "studentGenderList": StudentGenderList.objects.using(db_name).all().values(),
        "studentReligionList": StudentReligionList.objects.using(db_name)
        .all()
        .values(),
        "schoolTypeList": SchoolTypeList.objects.using(db_name).all().values(),
        "controlList": ControlList.objects.using(db_name).all().values(),
        "nationalityList": NationalityList.objects.using(db_name).all().values(),
        "languagesList": LanguagesList.objects.using(db_name).all().values(),
        "schoolCodeList": SchoolCodeList.objects.using(db_name).all().values(),
    }
    filters_data = {}
    if "*" in selected_filters:
        for key in query_dict:
            filters_data[key] = list(query_dict[key])
    else:
        for key in selected_filters:
            query = query_dict.get(key)
            if query:
                filters_data[key] = list(query)
    return filters_data
