import logging

from rest_framework import status
from rest_framework.exceptions import APIException

from core.utils.messages import EXCEPTIONS


class LoggedAPIException(APIException):
    def __init__(self, detail=None, code=None, log=True):
        if log:
            logger = logging.getLogger("ExceptionLogger")
            logger.info(self, exc_info=False)
        super().__init__(detail, code)


class InvalidResetTokenError(LoggedAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = EXCEPTIONS.get('EMAIL_TOKEN_EXPIRED')
    default_code = 'invalid_token_error'


class InvalidParamsError(LoggedAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = EXCEPTIONS.get('INCOMPLETE_ERROR')
    default_code = 'invalid_params_passed'


class UnprocessableParamsError(LoggedAPIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = EXCEPTIONS.get('UNPROCESSABLE_ERROR')
    default_code = 'unprocessable_params_error'


class ValidationError(LoggedAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = EXCEPTIONS.get('VALIDATION_ERROR')
    default_code = 'invalid_params_passed'


class AuthenticationError(LoggedAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = EXCEPTIONS.get('AUTH_ERROR')
    default_code = 'authentication_failed'


class PermissionError(LoggedAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = EXCEPTIONS.get('FORBIDDEN_ERROR')
    default_code = 'permission_required_error'


class NotFoundError(LoggedAPIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = EXCEPTIONS.get('NOT_FOUND_ERROR')
    default_code = 'resourse_not_found_error'


class MethodNotAllowedError(APIException):
    status_code = status.HTTP_405_METHOD_NOT_ALLOWED
    default_detail = EXCEPTIONS.get('REQUEST_METHOD_ERROR')
    default_code = 'method_not_allowed'

    def __init__(self, method, detail=None, code=None):
        if detail is None:
            detail = self.default_detail.format(method=method)
        super().__init__(detail, code)


class InternalServerError(LoggedAPIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = EXCEPTIONS.get('INTERNAL_ERROR')
    default_code = 'internal_server_error'
