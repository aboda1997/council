from core.helpers.general import run_sql_command
from core.models.db import FacultyName, Status, Years
from core.utils.enums import SemesterEnum, StageEnum, StudentStatus, UniversityTypeEnum


def get_table_columns():
    status_names = list(
        Status.objects.filter(
            id__in=[
                StudentStatus.ACCEPTED.value,
                StudentStatus.FULFILLMENT.value,
                StudentStatus.REJECTED.value,
            ]
        ).values("id", "name")
    )
    return status_names


def get_profile_seats(university_id, year_id, registration_types):
    # Note: Maybe allow semester & stage to be dynamic later on.
    sql_params = [
        university_id,
        year_id,
        SemesterEnum.FIRST.value,
        StageEnum.FIRST.value,
    ]
    sql_query = """
        SELECT
            faculties.id as id,
            facultyname.id fac_type_id,
            facultyname.name fac_type_name,
            SUM( facultyseatsprofiles.seats ) allocated_seats
        FROM
            facultyseatsprofiles,
            facultyprofiles,
            facultyname,
            faculties
        WHERE
            facultyseatsprofiles.facultyProfile_id = facultyprofiles.id
            AND facultyprofiles.faculty_id = faculties.id
            AND facultyname.id = faculties.facultyname_id
            AND faculties.univ_id = %s
            AND facultyprofiles.year_id = %s
            AND facultyprofiles.semester_id = %s
            AND facultyprofiles.stage_id = %s
    """

    if registration_types:
        sql_query += """ AND facultyseatsprofiles.registrationType_id IN %s """
        sql_params.append(registration_types)

    sql_query += """
        GROUP BY
            faculties.univ_id,
            faculties.facultyname_id
        ORDER BY
            faculties.facultyname_id
    """
    data = run_sql_command(sql_query, sql_params, 3)
    return data


def get_student_counts(university_id, year_id, registration_types):
    sql_params = [
        university_id,
        year_id,
        [
            StudentStatus.ACCEPTED.value,
            StudentStatus.FULFILLMENT.value,
            StudentStatus.REJECTED.value,
        ],
    ]

    sql_query = """
        SELECT
            1 as id,
            faculties.facultyname_id fac_type_id,
            faculties.name fac_type_name,
            status.id status_id,
            status.name status_name,
            COUNT( studentsuniversityedu.id ) actual_seats
        FROM
            studentsuniversityedu,
            students,
            faculties,
            facultyname,
            status
        WHERE
            studentsuniversityedu.studentFaculty_id = faculties.id
            AND facultyname.id = faculties.facultyname_id
            AND studentsuniversityedu.student_id = students.id
            AND students.studentStatus_id = status.id
            AND studentsuniversityedu.studentUniveristy_id = %s
            AND studentsuniversityedu.studentEnrollYear_id = %s
            AND students.studentStatus_id IN %s
    """

    if registration_types:
        sql_query += """ AND studentsuniversityedu.studentRegistrationType_id IN %s """
        sql_params.append(registration_types)

    sql_query += """
        GROUP BY
            studentsuniversityedu.studentUniveristy_id,
            faculties.facultyname_id,
            students.studentStatus_id
    """
    data = run_sql_command(sql_query, sql_params, 3)
    return data


def format_report_data(seats_data, counts_data):
    data_dict = {}
    for record in seats_data:
        fac_type_id = record.fac_type_id or "0"
        if not data_dict.get(fac_type_id):
            data_dict[fac_type_id] = {
                "fac_type_id": record.fac_type_id,
                "fac_type_name": record.fac_type_name,
                "allocated_seats": record.allocated_seats,
                "remaining": record.allocated_seats,
            }
    for record in counts_data:
        fac_type_id = record.fac_type_id or "0"
        if not data_dict.get(fac_type_id):
            data_dict[fac_type_id] = {
                "fac_type_id": record.fac_type_id,
                "fac_type_name": record.fac_type_name,
            }
        data_dict[fac_type_id][str(record.status_id) + "_actual_seats"] = int(
            record.actual_seats
        )
        remaining = data_dict.get(fac_type_id).get("remaining") or 0
        data_dict[fac_type_id]["remaining"] = int(remaining) - int(record.actual_seats)

    return data_dict.values()


def get_report_data(university_id=None, year_id=None, registration_types=None):
    if isinstance(registration_types, str):
        registration_types = registration_types.split(",")
    seats_data = get_profile_seats(university_id, year_id, registration_types)
    counts_data = get_student_counts(university_id, year_id, registration_types)
    return {
        "columns": get_table_columns(),
        "reportData": format_report_data(seats_data, counts_data),
    }
