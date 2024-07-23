from django.http import HttpResponse
from rest_framework import status
from rest_framework.response import Response
from wsgiref.util import FileWrapper

from core.utils.messages import MESSAGES, SERVICE_MESSSAGES


class APIResponse(Response):
    default_status_code = status.HTTP_200_OK
    default_detail = MESSAGES.get('DEFAULT_OKAY')

    """
    Alters the init arguments slightly of the Rest Framwork Response, to include a message.
    """

    def __init__(self, status=None, detail=None, **payload):
        if status is None:
            status = self.default_status_code
        if detail is None:
            detail = self.default_detail
        data = {'detail': detail, **payload}
        return super().__init__(status=status, data=data)


class FileResponse(HttpResponse):
    def __inti__(self, file, content_type):
        return super().__init__(FileWrapper(file), content_type=content_type)


class ServiceResponse(Response):
    default_status_code = status.HTTP_200_OK
    default_status = 'success'
    default_message = SERVICE_MESSSAGES.get("DEFAULT_OKAY")

    def __init__(self, status_code=None, status=None, message=None, **payload):
        if status_code is None:
            status_code = self.default_status_code

        data = {
            'status': status or self.default_status,
            'message': message or self.default_message,
        }

        if payload.get("data"):
            data['data'] = payload['data']
        else:
            data = {**data, **payload}

        return super().__init__(status=status_code, data=data)
