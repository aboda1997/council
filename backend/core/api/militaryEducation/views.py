from core.helpers.filters import get_council_filters
from core.helpers.general import get_request_summary
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse
from core.utils.views import ServerAPIView

from .controller import (
    add_military_data,
    delete_military_data,
    edit_military_data,
    get_form_filters,
    get_military_data,
    get_military_list,
)


class Filters(ServerAPIView):
    def get(self, request):
        payload = get_council_filters(
            [
                "universities",
                "faculties",
            ]
        )
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class FormFilters(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get('Id', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        payload = get_form_filters(student_id)
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class Student(ServerAPIView):
    def get(self, request):
        student_id = request.query_params.get('Id', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        payload = get_military_data(student_id)
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)

    def post(self, request):
        user_id = request.user.get('id', None)
        student_id = request.data.get('Id', None)
        military_data = request.data.get('studentMilitaryEdu', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        if not military_data:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_MISSING'))
        detail = add_military_data(student_id, military_data, user_id)
        return APIResponse(detail=detail)

    def put(self, request):
        summary = get_request_summary(request)
        student_id = request.data.get('Id', None)
        military_data = request.data.get('studentMilitaryEdu', None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_ID'))
        if not military_data:
            raise InvalidParamsError(EXCEPTIONS.get('MISSING_STUDENT_MISSING'))
        detail = edit_military_data(student_id, military_data, summary)
        return APIResponse(detail=detail)

    def delete(self, request):
        student_id = request.data.get("Id", None)
        if not student_id:
            raise InvalidParamsError(EXCEPTIONS.get("MISSING_STUDENT_ID"))

        user_id = request.user.get("id", None)
        summary = get_request_summary(request)

        detail = delete_military_data(student_id, user_id, summary)
        return APIResponse(detail=detail)


class StudentsList(ServerAPIView):
    def get(self, request):
        page = request.query_params.get('page', 0)
        per_page = request.query_params.get('perPage', 10)
        payload = get_military_list(request.query_params, page, per_page)
        return APIResponse(
            detail=MESSAGES.get('DEFAULT_OKAY'),
            payload=payload,
        )
