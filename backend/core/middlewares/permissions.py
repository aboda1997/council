from rest_framework import permissions

from core.models.db import UserAppliction
from core.utils.enums import ApplicationEnum, RightEnum
from core.utils.exceptions import InternalServerError
from core.utils.messages import MESSAGES


class IsAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view) -> bool:
        if isinstance(request.user, dict):
            return bool(request.user.get('id') and request.user.get('username'))
        return bool(request.user.id and request.user.username)


class hasApplicationRight(permissions.BasePermission):
    """
    Allows access only to users that has specific app right.
    """

    def has_permission(self, request, view) -> bool:
        # Gets the parameters to check if user has the rights
        user_id = request.user.get('id', None)
        app_id = view.api_application
        right_id = view.api_method_rights.get(request.method, None)
        if not right_id:
            raise InternalServerError(MESSAGES.get('MISSING_RIGHT_ID'))
        if not app_id:
            app_id = self.get_api_app(request)
        # Converts Enum to Values, if given values are Enums
        if isinstance(app_id, ApplicationEnum):
            app_id = app_id.value
        if isinstance(right_id, RightEnum):
            right_id = right_id.value
        # if all values are given, it checks in the database.
        if user_id and app_id and right_id:
            user_right_query = ""
            if isinstance(app_id, str):
                user_right_query = UserAppliction.objects.filter(
                    user_id=user_id, app__name=app_id, right_id=right_id
                )
            else:
                user_right_query = UserAppliction.objects.filter(
                    user_id=user_id, app_id=app_id, right_id=right_id
                )
            if user_right_query.count() > 0:
                return True
        return False

    def get_api_app(self, request):
        path_parts = request.path.split('/')
        app_name = None
        if len(path_parts) > 2:
            app_name = path_parts[2]
        if not app_name:
            raise InternalServerError(MESSAGES.get('MISSING_APP_ID'))
        return app_name
