from core.helpers.filters import get_council_filters
from core.helpers.general import get_request_summary
from core.helpers.students_attachments import (
    get_student_attachment,
    create_student_attachments,
    delete_student_attachments,
)
from core.helpers.students import get_students_list
from core.utils.enums import StudentStatus
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse, FileResponse
from core.utils.views import ServerAPIView

from .controller import (
    get_faculty_data,
    get_student,
    get_transfer_filters,
    transfer_student,
)


class StudentsList(ServerAPIView):
    def get(self, request):
        params = request.query_params.dict()
        page = params.get("page", 0)
        per_page = params.get("perPage", 10)

        # Filter students to return students with allowed status to transfer
        if not params.get("studentStatus"):
            params["studentStatus"] = [
                *StudentStatus.ACCEPTANCE_STATUS.value,
                StudentStatus.WITHDRAWN.value,
            ]

        payload = get_students_list(params, page, per_page)
        return APIResponse(
            detail=MESSAGES.get("DEFAULT_OKAY"),
            payload=payload,
        )


class Student(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get("Id")
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_ID"))
        payload = get_student(student_id)
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class Filters(ServerAPIView):
    def get(self, request):
        payload = get_council_filters(
            [
                "years",
                "semesters",
                "stages",
                "certificates",
                "countries",
                "universities",
                "faculties",
                "status",
                "fulfillments",
                "registrationTypes",
            ]
        )
        # Can transfer only students with status (accepted or under fulfillment)
        payload["status"] = list(
            filter(
                lambda s: s.get("id")
                in [
                    *StudentStatus.ACCEPTANCE_STATUS.value,
                    StudentStatus.WITHDRAWN.value,
                ],
                payload.get("status"),
            )
        )
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class FormFilters(ServerAPIView):
    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        university_id = request.query_params.get("university_id")
        payload = get_transfer_filters(faculty_id, university_id)
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class FacultyData(ServerAPIView):
    def get(self, request):
        faculty_id = request.query_params.get("faculty_id")
        if not faculty_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_TRANSFER_FACULTY_ID"))
        payload = get_faculty_data(faculty_id)
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class Transfer(ServerAPIView):
    def put(self, request):
        summary = get_request_summary(request)

        user_id = request.user.get("id")
        student_id = request.data.get("Id")
        faculty_id = request.data.get("faculty_id")
        transfer_date = request.data.get("transfer_date")
        equivalent_hours = request.data.get("equivalent_hours")
        transfer_level = request.data.get("transfer_level")
        fulfillment_id = request.data.get("fulfillment_id")

        if not user_id:
            raise InvalidParamsError(MESSAGES.get('INVALID_AUTH_HEADER'))

        payload = transfer_student(
            user_id,
            student_id,
            faculty_id,
            transfer_date,
            equivalent_hours,
            transfer_level,
            fulfillment_id,
            summary,
        )
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class Attachments(ServerAPIView):
    def get(self, request):
        file_id = request.query_params.get("fileId", None)
        file_data = get_student_attachment(file_id)
        return FileResponse(
            file_data.get("file"), content_type=file_data.get("content_type")
        )

    def put(self, request):
        action = request.data.get("action")

        if action == "CREATE":
            user_id = request.user.get("id")
            student_unique_id = request.data.get("uniqueId")
            files = request.FILES.getlist("files")
            results = create_student_attachments(user_id, student_unique_id, files)
            return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=results)

        elif action == "DELETE":
            request_summary = get_request_summary(request)
            files_data = request.data.get("files")
            results = delete_student_attachments(files_data, request_summary)
            return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=results)

        else:
            raise InvalidParamsError(EXCEPTIONS.get("INVALID_POST_ATTACHMENT_REQUEST"))
