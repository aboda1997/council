from core.helpers.filters import get_council_filters
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse
from core.utils.views import ServerAPIView

from .controller import get_report_data


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
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class Report(ServerAPIView):
    def get(self, request):
        params = request.query_params.dict()
        if not params.get("university"):
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))
        payload = get_report_data(params)
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)
