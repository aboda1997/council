import environ
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from jwt import ExpiredSignatureError

from core.helpers.general import log_activity, log_user_auth
from core.helpers.hasher import hash_password, verify_password
from core.helpers.tokenizer import decode_token, generate_token
from core.models.db import User, UserAppliction
from core.utils.enums import TokenType
from core.utils.exceptions import InvalidParamsError, InvalidResetTokenError
from core.utils.messages import EXCEPTIONS


def login_user(username: str, password: str, summary: dict[str:any] = None):
    user: User = None
    # Validates User Data and tries to get them from db
    MAX_CHAR_LENGTH = 50
    if len(username) > MAX_CHAR_LENGTH or len(password) > MAX_CHAR_LENGTH:
        raise InvalidParamsError(
            EXCEPTIONS.get('INVALID_AUTH_LENGTH').format(max=MAX_CHAR_LENGTH)
        )
    try:
        user = User.objects.get(Q(username__exact=username) | Q(email__exact=username))
    except (ObjectDoesNotExist):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_AUTH_USER'))
    if not verify_password(password, user.password):
        raise InvalidParamsError(EXCEPTIONS.get('INVALID_AUTH_PARAMS'))

    # Generates Access Token for the user.
    token_payload = {'id': user.id, 'username': user.username}
    auth_token = generate_token(token_payload)

    # Gets Application the User has Access to.
    user_permissions = get_user_permissions(user.id)
    # Formates other user data to be sent back to the front.
    user_data = {
        'username': user.username,
        'fullname': user.fullname,
        'nid': user.nid,
        'email': user.email,
    }
    if summary:
        summary["USER_ID"] = user.id
        log_user_auth("User login", summary)
    return {
        'accessToken': auth_token,
        'userPermissions': user_permissions,
        'userData': user_data,
    }


def get_user_permissions(user_id: str):
    # Gets user permissions from the database
    user_permissions = list(
        UserAppliction.objects.filter(user_id=user_id).values(
            'app__id',
            'app__name',
            'app__icon',
            'app__displayName',
            'app__category__id',
            'app__category__name',
            'app__category__icon',
            'app__category__displayName',
            'right_id',
        )
    )
    # Formates user permissions into two objects
    app_categories = {}
    user_applications = {}
    for permission in user_permissions:
        if permission['app__category__id']:
            app_categories[permission['app__category__id']] = {
                "id": permission['app__category__id'],
                "name": permission['app__category__name'],
                "displayName": permission['app__category__displayName'],
                "icon": permission['app__category__icon'],
            }
        if not (user_applications.get(permission['app__id'], None)):
            user_applications[permission['app__id']] = {
                "id": permission['app__id'],
                "name": permission['app__name'],
                "icon": permission['app__icon'],
                "displayName": permission['app__displayName'],
                "categoryId": permission['app__category__id'],
                "rights": [],
            }
        if permission['right_id']:
            user_applications[permission['app__id']]["rights"].append(
                permission['right_id']
            )
    return {
        "appCategories": app_categories.values(),
        "userApplications": user_applications.values(),
    }


def forget_password(to: str, lang: str):
    env = environ.Env()
    check_email = User.objects.get(email__exact=to)
    token_payload = {'email': to}
    auth_token = generate_token(token_payload, token_type=TokenType.RESET_TOKEN)
    token = auth_token
    check_email.token = auth_token
    check_email.save()
    if lang == "ar":
        html_content = render_to_string(
            "email_template_ar.html",
            {'resetToken': env('SERVER_LINK') + token},
        )
    else:
        html_content = render_to_string(
            "email_template_en.html",
            {'resetToken': env('SERVER_LINK') + token},
        )
    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(
        # subject
        "Reset Password",
        # html_content
        text_content,
        # from email
        settings.EMAIL_HOST_USER,
        # rec
        [to],
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def verify_email_token(self, raw_token: str) -> dict[str, any]:
    try:
        payload = decode_token(raw_token)
    except ExpiredSignatureError:
        # If token is only invalid because of its expiration
        raise InvalidResetTokenError()
    except Exception:
        raise InvalidResetTokenError(detail=EXCEPTIONS.get('EMAIL_TOKEN_INVALID'))
    return {'email': payload.get('email')}


def store_password(password: str, email_token: str, summary: dict[str, any] = None):
    user_query = User.objects.filter(token__exact=email_token)
    user_data = user_query.values().first()
    hashed_pass = str(hash_password(password))
    final_hashed_pass = hashed_pass.lstrip("b\'").rstrip("\'")
    if summary:
        summary["USER_ID"] = user_data.get("id")
        log_activity("User Password Change", user_data, summary)
    user_query.update(
        updatedAt=timezone.now(),
        updatedBy=user_data.get("id"),
        password=final_hashed_pass,
        token=None,
    )
