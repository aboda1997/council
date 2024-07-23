from core.helpers.filters import get_council_filters, get_gs_filters
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse
from core.utils.views import ServerAPIView

from .controller import (
    add_cd_student,
    delete_cd_student,
    edit_cd_student,
    get_cd_student,
    get_cd_students_list,
)


class Filters(ServerAPIView):
    def get(self, request):
        payload = get_council_filters(["years"])
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class GSFilters(ServerAPIView):
    def get(self, request):
        year_code = request.query_params.get('selectedYear', None)
        if year_code:
            payload = get_gs_filters(year_code)
            return APIResponse(payload=payload)
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))


class CDStudent(ServerAPIView):
    def get(self, request):
        year_code = request.query_params.get('selectedYear', None)
        national_id = request.query_params.get('nationalId', None)
        seat_num = request.query_params.get('seatNumber', None)
        if year_code and (national_id or seat_num):
            payload = get_cd_student(year_code, national_id, seat_num)
            return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))

    def post(self, request):
        year_code = request.data.get('selectedYear', None)
        student_data = request.data.get('student', None)
        if year_code and student_data:
            detail = add_cd_student(year_code, student_data)
            return APIResponse(detail=detail)
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))

    def put(self, request):
        year_code = request.data.get('selectedYear', None)
        national_id = request.data.get('nationalId', None)
        seat_num = request.data.get('seatNumber', None)
        student_data = request.data.get('student', None)
        if year_code and student_data and (national_id or seat_num):
            detail = edit_cd_student(year_code, national_id, seat_num, student_data)
            return APIResponse(detail=detail)
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))

    def delete(self, request):
        year_code = request.data.get('selectedYear', None)
        national_id = request.data.get('nationalId', None)
        seat_num = request.data.get('seatNumber', None)
        if year_code and (national_id or seat_num):
            detail = delete_cd_student(year_code, national_id, seat_num)
            return APIResponse(detail=detail)
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))


class CDStudentsList(ServerAPIView):
    def get(self, request):
        year = request.query_params.get('selectedYear', None)
        search_type = request.query_params.get('searchType', None)
        search_input = request.query_params.get('searchField', None)
        page = request.query_params.get('page', 0)
        per_page = request.query_params.get('perPage', 10)
        if year and search_type and search_input and page and per_page:
            payload = get_cd_students_list(
                year, search_type, search_input, page, per_page
            )
            return APIResponse(
                detail=MESSAGES.get('DEFAULT_OKAY'),
                payload=payload,
            )
        else:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))
