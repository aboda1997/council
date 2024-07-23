from core.helpers.filters import get_council_filters
from core.helpers.general import get_request_summary
from core.helpers.students_attachments import (
    get_student_attachment,
    create_student_attachments,
    delete_student_attachments,
)
from core.helpers.students import get_student, get_student_history, get_students_list
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse, FileResponse
from core.utils.views import ServerAPIView

from .controller import delete_student, edit_student


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
                "fulfillments",
                "registrationTypes",
            ]
        )
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class FormFilters(ServerAPIView):
    def get(self, request):
        payload = get_council_filters(
            [
                "countries",
                "religions",
                "genders",
                "governorates",
                "certificates",
                "years",
                "months",
                "stages",
                "semesters",
                "studyGroups",
                "status",
                "fulfillments",
                "universities",
                "faculties",
                "imposedCourses",
                "grades",
                "levels",
                "registrationTypes",
            ]
        )
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)


class Student(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get("Id", None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_ID"))
        payload = get_student(
            student_id,
            "graduate",
            show_graduation_data=True,
            show_prev_transfer_data=True,
        )
        return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=payload)

    def put(self, request):
        summary = get_request_summary(request)
        student_id = request.data.get("Id", None)
        student_data = request.data.get("studentData", None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_ID"))
        if not student_data:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_MISSING"))
        detail = edit_student(student_id, student_data, summary)
        return APIResponse(detail=detail)

    def delete(self, request):
        summary = get_request_summary(request)
        student_id = request.data.get("Id", None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_ID"))
        detail = delete_student(student_id, summary)
        return APIResponse(detail=detail)


class StudentHistory(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get('Id', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        payload = get_student_history(student_id, "graduate")
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class StudentsList(ServerAPIView):
    def get(self, request):
        page = request.query_params.get("page", 0)
        per_page = request.query_params.get("perPage", 10)
        params = request.query_params.dict()
        params["selectedStudentType"] = "graduate"
        payload = get_students_list(params, page, per_page)
        return APIResponse(
            detail=MESSAGES.get("DEFAULT_OKAY"),
            payload=payload,
        )


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
            results = create_student_attachments(
                user_id, student_unique_id, files, "graduate"
            )
            return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=results)

        elif action == "DELETE":
            request_summary = get_request_summary(request)
            files_data = request.data.get("files")
            results = delete_student_attachments(files_data, request_summary)
            return APIResponse(detail=MESSAGES.get("DEFAULT_OKAY"), payload=results)

        else:
            raise InvalidParamsError(EXCEPTIONS.get("INVALID_POST_ATTACHMENT_REQUEST"))
