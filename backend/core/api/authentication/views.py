from core.helpers.general import get_request_summary
from core.middlewares.permissions import IsAuthenticated
from core.models.db import User
from core.utils.exceptions import InvalidParamsError
from core.utils.messages import EXCEPTIONS, MESSAGES
from core.utils.responses import APIResponse
from core.utils.views import PublicServerAPIView, ServerAPIView

from .controller import (
    forget_password,
    get_user_permissions,
    login_user,
    store_password,
    verify_email_token,
)


class Login(PublicServerAPIView):
    def post(self, request):
        summary = get_request_summary(request)
        username = request.data.get('username', "None")
        password = request.data.get('password', None)
        if not (username and password):
            raise InvalidParamsError(EXCEPTIONS.get('AUTH_MISSING_DATA'))
        payload = login_user(username, password, summary)
        return APIResponse(detail=MESSAGES.get('LOGIN_SUCESSFUL'), payload=payload)


class UserPermissions(ServerAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.get('id', None)
        if not (user_id):
            raise InvalidParamsError(MESSAGES.get('INVALID_AUTH_HEADER'))
        user_permissions = get_user_permissions(user_id)
        payload = {"userPermissions": user_permissions}
        return APIResponse(detail=MESSAGES.get('LOGIN_SUCESSFUL'), payload=payload)


class ForgetPassword(PublicServerAPIView):
    # Function for checking the user input email "to" variable and the lanague "lang" variable in the databases
    # and create token for it if it exists and store it in the databases
    # if not raise error with message
    # if "lang" is arabic it will send the arabic email template, else the english one
    def post(self, request):
        to_email = request.data.get('email', None)
        lang = request.data.get('lang', None)
        try:
            forget_password(to_email, lang)
            return APIResponse(
                detail=MESSAGES.get('RESET_PASSWORD_EMAIL_SUCESSFUL'),
                payload=to_email,
            )
        except (Exception):
            raise InvalidParamsError(MESSAGES.get('INVALID_EMAIL_PARAMS'))


class CheckToken(PublicServerAPIView):
    # Check token whether or not is valid and is avaiable in database
    def post(self, request):
        try:
            token_email = request.data.get('emailToken', None)
            if User.objects.get(token__exact=token_email) is None:
                raise InvalidParamsError(MESSAGES.get('INVALID_TOKEN'))
            else:
                token_status = verify_email_token(self, raw_token=token_email)
                return APIResponse(
                    detail=MESSAGES.get('VALID_TOKEN'), payload=token_status
                )
        except (Exception):
            raise InvalidParamsError(MESSAGES.get('INVALID_TOKEN'))


class SavePassword(PublicServerAPIView):
    # Take Password and confirm password from the user with the token and check them,
    # if all good, then it will store the password
    def post(self, request):
        summary = get_request_summary(request)
        password = request.data.get('password', None)
        re_password = request.data.get('rePassword', None)
        email_token = request.data.get('emailToken', None)
        if (
            password == re_password
            and len(password) >= 8
            and len(re_password) >= 8
            and len(password) <= 50
            and len(re_password) <= 50
            and len(re_password) == len(password)
        ):
            try:
                store_password(re_password, email_token, summary)
                return APIResponse(detail=MESSAGES.get('RESET_PASSWORD_SUCCESS'))
            except (Exception):
                raise InvalidParamsError(EXCEPTIONS.get('RESET_PASSWORD_FAIL'))
        else:
            raise InvalidParamsError(MESSAGES.get('INVALID_PASSWORD_PARAMS'))
