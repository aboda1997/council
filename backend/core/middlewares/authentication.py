import environ
from jwt.exceptions import ExpiredSignatureError
from rest_framework import authentication

from core.helpers.tokenizer import decode_token, generate_token
from core.utils.exceptions import AuthenticationError, ValidationError
from core.utils.messages import EXCEPTIONS, SERVICE_MESSSAGES


class StatelessTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = self.get_authorization_header(request)
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        user_data = self.verify_token(raw_token)
        self.generate_access_token(user_data, request)
        return (user_data, None)

    def get_authorization_header(self, request) -> str:
        return request.META.get('HTTP_AUTHORIZATION', '')

    def get_raw_token(self, header: str) -> str:
        parts = header.split()

        if len(parts) == 0:
            # Empty AUTHORIZATION header sent
            return None

        if parts[0] not in ("Bearer", "Token"):
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            # Assumes that Authentication is invalid because has more than 2 parts
            raise AuthenticationError(detail=EXCEPTIONS.get('INVALID_AUTH_HEADER'))

        return parts[1]

    def verify_token(self, raw_token: str) -> dict[str, any]:
        try:
            payload = decode_token(raw_token)
        except ExpiredSignatureError:
            # If token is only invalid because of its expiration
            raise AuthenticationError()
        except Exception:
            raise AuthenticationError(detail=EXCEPTIONS.get('INVALID_AUTH_HEADER'))
        return {'id': payload.get('id'), 'username': payload.get('username')}

    def generate_access_token(self, token_payload, request):
        # Generate a new access token to be sent back in the response
        auth_token = generate_token(token_payload)
        request.META['NEW_ACCESS_TOKEN'] = auth_token


class ServiceTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        token = request.data.get('token')

        if not token:
            raise AuthenticationError(detail=SERVICE_MESSSAGES.get('MISSING_TOKEN'))

        service_token = environ.Env()('SERVICE_TOKEN')

        if token != service_token:
            raise ValidationError(detail=SERVICE_MESSSAGES.get('INVALID_TOKEN'))

        return None


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before reaching the view.
        response = self.get_response(request)
        # Code to be executed for each request/response after response is returned from view.
        new_token = request.META.get('NEW_ACCESS_TOKEN')
        if new_token:
            response.headers['Authorization'] = new_token
        return response
