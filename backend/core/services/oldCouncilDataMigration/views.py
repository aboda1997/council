import os
import collections
import json
from json import JSONDecodeError

import requests
from requests import ConnectionError

from core.models.db import (
    Certificates,
    Faculties,
    Gender,
    Grades,
    Months,
    Regions,
    RegistrationType,
    Status,
    StudyGroups,
    Universities,
    User,
    Years,
)
from core.services.oldCouncilDataMigration.constants import (
    DEFAULT_FLAGS,
    DEFAULT_MODE,
    FACULTIES_LOCAL_URL,
    FACULTIES_REMOTE_URL,
    MESSAGES,
    MODES,
)
from core.utils.enums import RegistrationTypeEnum
from core.utils.exceptions import InvalidParamsError
from core.utils.responses import ServiceResponse
from core.utils.views import ServiceAPIView

from .controller import add_students, update_invalid_students
from .test_students_data import test_students, test_invalid_students


class getStudentsByFaculty(ServiceAPIView):
    def post(self, request):
        # mode: report (default) | store | test
        mode = request.data.get("mode", DEFAULT_MODE)
        # source: remote (default) | local (port:3333)
        source = request.data.get("source", "remote")
        faculties_ids = request.data.get("faculties_ids")
        error_flags = request.data.get("error_flags", DEFAULT_FLAGS)
        output_flags = request.data.get("output_flags", DEFAULT_FLAGS)

        output_path = "/home/gitlab-runner/apps/council/backend/migration-results"

        if not isinstance(faculties_ids, list):
            raise InvalidParamsError(
                "Invalid data format, the request must contain a token and faculties ids list"
            )

        data = []
        status = "success"

        # total count for all faculties
        total_students_count = 0

        council_ids_map = None

        for faculty_id in faculties_ids:
            student_result = {}
            students_data = None

            student_result["status"] = "failed"

            target_faculty = (
                Faculties.objects.filter(oldcouncilid=faculty_id)
                .values("id", "oldcouncilid", "univ_id", "name")
                .first()
            )

            # check if faculty_id exists in faculties table (oldcouncilid)
            if target_faculty:
                try:
                    target_url = (
                        FACULTIES_REMOTE_URL
                        if source == "remote"
                        else FACULTIES_LOCAL_URL
                    )

                    response = requests.get(target_url.format(faculty_id=faculty_id))

                    students_data = response.json(strict=False)
                except ConnectionError as connection_error:
                    print(connection_error)
                    student_result["message"] = (
                        MESSAGES.get("CONNECTION_FAILURE")
                        + ", "
                        + str(connection_error)
                    )
                except JSONDecodeError as json_decode_error:
                    print(json_decode_error)
                    student_result["message"] = (
                        MESSAGES.get("INVALID_JSON_FORMAT")
                        + ", "
                        + str(json_decode_error)
                    )
                else:
                    if (
                        not students_data
                        or "students" not in students_data
                        or not isinstance(students_data.get("students"), list)
                    ):
                        student_result["message"] = MESSAGES.get("INVALID_DATA_FORMAT")
                    else:
                        student_result["status"] = "success"
                        students_list = students_data.get("students")
                        total_students_count = total_students_count + len(students_list)
                        if mode == MODES.get("TEST"):
                            student_result = {
                                **student_result,
                                **test_students(target_faculty, students_list),
                            }
                        else:
                            if not council_ids_map:
                                council_ids_map = create_council_tables_map(
                                    get_council_tables()
                                )
                            student_result = {
                                **student_result,
                                **add_students(
                                    target_faculty,
                                    students_list,
                                    council_ids_map,
                                    mode,
                                    error_flags,
                                    output_flags,
                                ),
                            }
            else:
                student_result["message"] = MESSAGES.get("FACULTY_NOT_FOUND").format(
                    faculty_id=faculty_id
                )

            data.append(student_result)

            with open(
                f"{output_path}/{faculty_id}_{mode}.json", "w", encoding="utf-8"
            ) as outfile:
                json.dump(student_result, outfile, ensure_ascii=False)

        message = generate_final_message(
            mode, data, len(faculties_ids), total_students_count
        )

        return ServiceResponse(message=message, data=data, status=status)


class updateInvalidStudents(ServiceAPIView):
    def post(self, request):
        # mode: store (default) | test
        mode = request.data.get("mode", DEFAULT_MODE)
        error_flags = request.data.get("error_flags", DEFAULT_FLAGS)

        # input_path = "./migration-data"
        # output_path = "./migration-results"

        input_path = "/home/gitlab-runner/apps/council/backend/migration-data"
        output_path = "/home/gitlab-runner/apps/council/backend/migration-results"
        input_file_name = "students_v2.json"
        output_file_name = f"update_students_{mode}"

        if not os.path.exists(output_path):
            message = f"output directory does not exist, `{input_path}`"
            return ServiceResponse(message=message, data=None, status="failed")

        if not os.path.isfile(f"{input_path}/{input_file_name}"):
            message = (
                f"Data source file does not exist, `{input_path}/{input_file_name}`"
            )
            return ServiceResponse(message=message, data=None, status="failed")

        data = []
        status = "success"

        students_list = None
        try:
            with open(f"{input_path}/{input_file_name}", "r", encoding="utf-8") as file:
                students_list = json.load(file)
        except IOError as error:
            message = (
                f"Error while reading data file from `{input_path}/{input_file_name}`, "
                + str(error)
            )
            return ServiceResponse(message=message, data=data, status="failed")

        council_ids_map = create_council_tables_map(get_council_tables())

        if not students_list or not isinstance(students_list, list):
            status = "failed"
            message = MESSAGES.get("INVALID_DATA_FORMAT")
        else:
            status = "success"
            message = {"mode": mode, "total_students_count": len(students_list)}
            if mode == MODES.get("TEST"):
                data = test_invalid_students(students_list)
            else:
                data = update_invalid_students(
                    students_list, council_ids_map, error_flags
                )

            if data:
                if os.path.exists(f"{output_path}/{output_file_name}.json"):
                    with open(
                        f"{output_path}/{output_file_name}.json",
                        "w",
                        encoding="utf-8",
                    ) as output_file:
                        json.dump(data, output_file, ensure_ascii=False)

        return ServiceResponse(message=message, data=data, status=status)


class getRepeatedStudents(ServiceAPIView):
    def post(self, request):
        faculties_ids = request.data.get("faculties_ids")

        if not isinstance(faculties_ids, list):
            raise InvalidParamsError(
                "Invalid data format, the request must contain a token and faculties ids list"
            )

        message = "Operation successfully completed"
        data = {}
        status = "success"

        for faculty_id in faculties_ids:
            student_result = {}
            students_data = None

            student_result["status"] = "failed"

            try:
                response = requests.get(
                    FACULTIES_REMOTE_URL.format(faculty_id=faculty_id)
                )

                students_data = response.json(strict=False)
            except ConnectionError as connection_error:
                print(connection_error)
                student_result["message"] = (
                    MESSAGES.get("CONNECTION_FAILURE") + ", " + str(connection_error)
                )
            except JSONDecodeError as jsonDecodeError:
                print(jsonDecodeError)
                student_result["message"] = (
                    MESSAGES.get("INVALID_JSON_FORMAT") + ", " + str(jsonDecodeError)
                )
            else:
                if (
                    not students_data
                    or "students" not in students_data
                    or not isinstance(students_data.get("students"), list)
                ):
                    student_result["message"] = MESSAGES.get("INVALID_DATA_FORMAT")
                else:
                    student_result["status"] = "success"
                    students_ids = []
                    repeated_ids = []
                    repeated_students = {}

                    for student in students_data.get("students"):
                        students_ids.append(student.get("student").get("id"))

                    repeated_ids = [
                        id
                        for id, count in collections.Counter(students_ids).items()
                        if count > 1
                    ]

                    for student in students_data.get("students"):
                        id = student.get("student").get("id")
                        if id in repeated_ids:
                            repeated_list = repeated_students.get(str(id), []) or []
                            repeated_list.append(student)
                            repeated_students[str(id)] = repeated_list

                    data = {
                        **data,
                        faculty_id: {
                            "ids_count": len(students_ids),
                            "repeated_count": len(repeated_ids),
                            "repeated_ids": repeated_ids,
                            "repeated_students": repeated_students,
                        },
                    }

        return ServiceResponse(message=message, data=data, status=status)


def create_council_tables_map(council_tables: dict[str, any]):
    """
    create a dict for every table where the {key: value} is {oldcouncilid: id}
    """
    council_maps = {}
    for table_name, table_records in council_tables.items():
        formatted_dict = {}
        for record in table_records:
            formatted_dict[record.get("oldcouncilid")] = record.get("id")
        council_maps[table_name] = formatted_dict

    years_codes = {}
    for record in council_tables.get("years"):
        years_codes[record.get("oldcouncilid")] = record.get("code")
    council_maps["years_codes"] = years_codes

    # special cases
    council_maps["faculties"]["0"] = None

    council_maps["universities"]["0"] = None
    council_maps["universities"]["16"] = None

    council_maps["years"]["0"] = None
    council_maps["months"]["0"] = None
    council_maps["gender"]["2"] = None
    council_maps["status"]["6"] = 6

    # {"cert_id": ["43", "44"], "fixed_cert_id": 42},
    council_maps["certificates"]["43"] = 34
    council_maps["certificates"]["44"] = 34
    # {"cert_id": ["50"], "fixed_cert_id": 51},
    council_maps["certificates"]["50"] = 41
    # {"cert_id": ["53"], "fixed_cert_id": 52},
    council_maps["certificates"]["53"] = 42
    # {"cert_id": ["69"], "fixed_cert_id": 70},
    council_maps["certificates"]["69"] = 58
    # {"cert_id": ["102", "112"], "fixed_cert_id": 99},
    council_maps["certificates"]["102"] = 86
    council_maps["certificates"]["112"] = 86
    # {"cert_id": ["77"], "fixed_cert_id": None},
    council_maps["certificates"]["77"] = None

    # `registrationtype = -1` transferred students -> transfer
    council_maps["registrationtype"]["-1"] = RegistrationTypeEnum.TRANSFER.value

    return council_maps


def get_council_tables():
    return {
        "certificates": Certificates.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "faculties": Faculties.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "gender": Gender.objects.all().values("id", "oldcouncilid"),
        "grades": Grades.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "months": Months.objects.all().values("id", "oldcouncilid"),
        "regions": Regions.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "registrationtype": RegistrationType.objects.filter().values(
            "id", "oldcouncilid"
        ),
        "status": Status.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "studygroups": StudyGroups.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "users": User.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "universities": Universities.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid"
        ),
        "years": Years.objects.filter(oldcouncilid__isnull=False).values(
            "id", "oldcouncilid", "code"
        ),
    }


def generate_final_message(mode, data, faculties_count, total_students_count):
    final_message = {
        "result": "Operation successfully completed",
        "mode": mode,
        "total_faculties_count": faculties_count,
        "total_students_count": total_students_count,
    }

    total_exist_students_count = 0
    total_replaced_count = 0
    total_passed_count = 0
    total_failed_count = 0

    for faculty_data in data:
        faculty_results = faculty_data.get("results")

        if faculty_results:
            total_exist_students_count += faculty_results.get("exist_students_count", 0)
            total_replaced_count += faculty_results.get("replaced_count", 0)
            total_passed_count += faculty_results.get("passed_count", 0)
            total_failed_count += faculty_results.get("failed_count", 0)

    if total_exist_students_count:
        final_message["total_exist_students_count"] = total_exist_students_count
    if total_replaced_count:
        final_message["total_replaced_count"] = total_replaced_count
    if total_passed_count:
        final_message["total_passed_count"] = total_passed_count
    if total_failed_count:
        final_message["total_failed_count"] = total_failed_count

    return final_message
