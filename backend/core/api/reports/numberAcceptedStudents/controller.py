from core.helpers.general import run_sql_command
from core.models.db import FacultyName, Years
from core.utils.enums import SemesterEnum, StageEnum, StudentStatus, UniversityTypeEnum


def get_table_columns():
    faculty_names = list(FacultyName.objects.all().values("id", "name"))
    return faculty_names


def get_profile_seats(year_id, registration_types):
    # Note: Maybe allow semester & stage to be dynamic later on.
    sql_params = [
        year_id,
        SemesterEnum.FIRST.value,
        StageEnum.FIRST.value,
        UniversityTypeEnum.NON_PRIVATE_NATIONAL.value,
    ]
    sql_query = """
        SELECT
            faculties.id as id,
            faculties.univ_id univ_id,
            universities.name univ_name,
            faculties.facultyname_id fac_type_id,
            SUM( facultyseatsprofiles.seats ) allocated_seats
        FROM
            facultyseatsprofiles,
            facultyprofiles,
            faculties,
            universities
        WHERE
            facultyseatsprofiles.facultyProfile_id = facultyprofiles.id
            AND facultyprofiles.faculty_id = faculties.id
            AND universities.id = faculties.univ_id
            AND facultyprofiles.year_id = %s
            AND facultyprofiles.semester_id = %s
            AND facultyprofiles.stage_id = %s
            AND universities.typeid NOT IN %s
    """

    if registration_types:
        sql_query += """ AND facultyseatsprofiles.registrationType_id IN %s """
        sql_params.append(registration_types)

    sql_query += """
        GROUP BY
            faculties.univ_id,
            faculties.facultyname_id
        ORDER BY
            faculties.univ_id
    """
    data = run_sql_command(sql_query, sql_params, 3)
    return data


def get_student_counts(year_id, registration_types):
    sql_params = [
        year_id,
        StudentStatus.ACCEPTANCE_STATUS.value,
        UniversityTypeEnum.NON_PRIVATE_NATIONAL.value,
    ]

    sql_query = """
        SELECT
            1 as id,
            universities.id univ_id,
            universities.name univ_name,
            faculties.facultyname_id fac_type_id,
            COUNT( studentsuniversityedu.id ) actual_seats
        FROM
            studentsuniversityedu,
            students,
            universities,
            faculties
        WHERE
            studentsuniversityedu.studentUniveristy_id = universities.id
            AND studentsuniversityedu.studentFaculty_id = faculties.id
            AND studentsuniversityedu.student_id = students.id
            AND studentsuniversityedu.studentEnrollYear_id = %s
            AND students.studentStatus_id IN %s
            AND universities.typeid NOT IN %s
    """

    if registration_types:
        sql_query += """ AND studentsuniversityedu.studentRegistrationType_id IN %s """
        sql_params.append(registration_types)

    sql_query += """
        GROUP BY
            studentsuniversityedu.studentUniveristy_id, faculties.facultyname_id
    """
    data = run_sql_command(sql_query, sql_params, 3)
    return data


def format_report_data(seats_data, counts_data):
    data_dict = {}
    for record in seats_data:
        univ_id = record.univ_id or "0"
        if not data_dict.get(univ_id):
            data_dict[univ_id] = {
                "univ_id": record.univ_id,
                "univ_name": record.univ_name,
            }
        data_dict[univ_id][str(record.fac_type_id) + "_allocated_seats"] = int(
            record.allocated_seats
        )
    for record in counts_data:
        univ_id = record.univ_id or "0"
        if not data_dict.get(univ_id):
            data_dict[univ_id] = {
                "univ_id": record.univ_id,
                "univ_name": record.univ_name,
            }
        data_dict[univ_id][str(record.fac_type_id) + "_actual_seats"] = int(
            record.actual_seats
        )

    return data_dict.values()


def get_report_data(year_id=None, registration_types=None):
    if not year_id:
        year_id = Years.objects.filter(current=1).values("id").first().get("id") or 0
    if isinstance(registration_types, str):
        registration_types = registration_types.split(",")
    seats_data = get_profile_seats(year_id, registration_types)
    counts_data = get_student_counts(year_id, registration_types)
    return {
        "columns": get_table_columns(),
        "reportData": format_report_data(seats_data, counts_data),
    }
