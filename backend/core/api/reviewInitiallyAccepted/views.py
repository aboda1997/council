from core.helpers.filters import get_council_filters
from core.helpers.general import get_request_summary
from core.helpers.students import get_students_list
from core.utils.enums import StudentStatus
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS
from core.utils.responses import APIResponse
from core.utils.views import ServerAPIView

from .controller import filter_form_filters, review_student_data


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
        return APIResponse(payload=payload)


class FormFilters(ServerAPIView):
    def get(self, request):
        payload = filter_form_filters(
            get_council_filters(
                [
                    "status",
                    "fulfillments",
                ]
            )
        )
        return APIResponse(payload=payload)


class ReviewStudents(ServerAPIView):
    def put(self, request):
        summary = get_request_summary(request)
        data = {
            "studentsIds": request.data.get("studentsIds"),
            "studentStatus": request.data.get("studentStatus"),
            "studentFulfillment": request.data.get("studentFulfillment"),
        }
        if not data.get("studentsIds"):
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_IDS"))
        if not data.get("studentStatus"):
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STATUS_IDS"))
        detail = review_student_data(data, summary)
        return APIResponse(detail=detail)


class StudentsList(ServerAPIView):
    def get(self, request):
        page = request.query_params.get("page", 0)
        per_page = request.query_params.get("perPage", 10)
        params = request.query_params.dict()
        params["selectedStudentType"] = None
        params["studentStatus"] = StudentStatus.INITIALLY_ACCEPTED.value
        payload = get_students_list(params, page, per_page)
        return APIResponse(payload=payload)
