from core.helpers.filters import get_council_filters
from core.helpers.general import get_request_summary
from core.helpers.students import get_student, get_students_list
from core.utils.enums import StudentStatus
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS
from core.utils.responses import APIResponse
from core.utils.views import ServerAPIView

from .controller import filter_form_filters, review_student_data, withdraw_graduation


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
                    "months",
                    "years",
                    "grades",
                ]
            )
        )
        return APIResponse(payload=payload)


class Student(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get('Id', None)
        selected_student_type = request.query_params.get(
            'selectedStudentType', "student"
        )
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        payload = get_student(
            student_id, selected_student_type, show_graduation_data=True
        )
        return APIResponse(payload=payload)

    def put(self, request):
        summary = get_request_summary(request)
        student_id = request.data.get('Id', None)
        student_data = request.data.get('studentData', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        if not student_data:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_MISSING'))
        detail = review_student_data(student_id, student_data, summary)
        return APIResponse(detail=detail)


class Withdraw(ServerAPIView):
    def put(self, request):
        summary = get_request_summary(request)
        student_id = request.data.get('Id', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        detail = withdraw_graduation(student_id, summary)
        return APIResponse(detail=detail)


class StudentsList(ServerAPIView):
    def get(self, request):
        selected_student_type = request.query_params.get("selectedStudentType", None)
        page = request.query_params.get("page", 0)
        per_page = request.query_params.get("perPage", 10)
        params = request.query_params.dict()

        if not selected_student_type:
            raise InvalidParamsError(EXCEPTIONS.get("INPUT_MISSING"))
        if selected_student_type == "student":
            params["studentStatus"] = StudentStatus.GRADUATION_APPLICANT.value

        payload = get_students_list(params, page, per_page)
        return APIResponse(payload=payload)
