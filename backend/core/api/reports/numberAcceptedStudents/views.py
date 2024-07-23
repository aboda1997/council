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
                "registrationTypes",
                "years",
            ]
        )
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)


class Report(ServerAPIView):
    def get(self, request):
        year = request.query_params.get("year", None)
        registration_types = request.query_params.get("registrationTypes", None)
        if not year:
            raise InvalidParamsError(EXCEPTIONS.get('INPUT_MISSING'))
        payload = get_report_data(year, registration_types)
        return APIResponse(detail=MESSAGES.get('DEFAULT_OKAY'), payload=payload)
