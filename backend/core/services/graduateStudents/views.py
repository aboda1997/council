from core.utils.exceptions import InvalidParamsError
from core.utils.messages import SERVICE_MESSSAGES
from core.utils.responses import ServiceResponse
from core.utils.views import ServiceAPIView

from .controller import graduate_students, withdraw_graduates


class ReceiveStudents(ServiceAPIView):
    def post(self, request):
        students = request.data.get("students")
        if not students or not isinstance(students, list):
            raise InvalidParamsError(SERVICE_MESSSAGES.get("INVALID_DATA_FORMAT"))
        data = graduate_students(students)
        return ServiceResponse(
            message=SERVICE_MESSSAGES.get("DEFAULT_OKAY"),
            data=data,
        )


class WithdrawStudents(ServiceAPIView):
    def post(self, request):
        students = request.data.get("students")
        if not students or not isinstance(students, list):
            raise InvalidParamsError(SERVICE_MESSSAGES.get("INVALID_DATA_FORMAT"))
        data = withdraw_graduates(students)
        return ServiceResponse(
            message=SERVICE_MESSSAGES.get("DEFAULT_OKAY"),
            data=data,
        )
