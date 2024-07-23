from rest_framework import permissions, views

from core.middlewares.authentication import ServiceTokenAuthentication
from core.middlewares.permissions import IsAuthenticated, hasApplicationRight
from core.utils.enums import RightEnum
from core.utils.exceptions import (
    AuthenticationError,
    MethodNotAllowedError,
    PermissionError,
)
from core.utils.messages import EXCEPTIONS


class ServerAPIView(views.APIView):
    permission_classes = [IsAuthenticated & hasApplicationRight]
    api_application = None
    api_method_rights = {
        'GET': RightEnum.VIEW,
        'POST': RightEnum.SAVE,
        'PUT': RightEnum.EDIT,
        'DELETE': RightEnum.DELETE,
    }

    # Overrides method to customize exception
    def http_method_not_allowed(self, request, *args, **kwargs):
        raise MethodNotAllowedError(request.method)

    def permission_denied(self, request, message=None, code=None):
        if request.authenticators and not request.successful_authenticator:
            raise AuthenticationError(detail=EXCEPTIONS.get('INVALID_AUTH_HEADER'))
        raise PermissionError()


class ServiceAPIView(ServerAPIView):
    authentication_classes = [ServiceTokenAuthentication]
    permission_classes = []


class PublicServerAPIView(ServerAPIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
