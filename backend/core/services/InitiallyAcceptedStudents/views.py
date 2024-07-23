from core.utils.exceptions import InvalidParamsError
from core.utils.messages import SERVICE_MESSSAGES
from core.utils.responses import ServiceResponse
from core.utils.views import ServiceAPIView

from .controller import add_student, remove_repeated_records, remove_student_records


class ReceiveStudents(ServiceAPIView):
    def post(self, request):
        students = request.data.get("students")
        if not students or not isinstance(students, list):
            raise InvalidParamsError(SERVICE_MESSSAGES.get("INVALID_DATA_FORMAT"))
        else:
            data = add_student(students)
            return ServiceResponse(
                message=SERVICE_MESSSAGES.get("DEFAULT_OKAY"),
                data=data,
            )


class WithdrawStudents(ServiceAPIView):
    def post(self, request):
        students = request.data.get("students")
        if not students or not isinstance(students, list):
            raise InvalidParamsError(SERVICE_MESSSAGES.get("INVALID_DATA_FORMAT"))
        else:
            data = remove_student_records(students)
            return ServiceResponse(
                message=SERVICE_MESSSAGES.get("DEFAULT_OKAY"),
                data=data,
            )


class RepeatedRecords(ServiceAPIView):
    def delete(self, request):
        data = remove_repeated_records()
        return ServiceResponse(
            message=SERVICE_MESSSAGES.get("DEFAULT_OKAY"),
            data=data,
        )