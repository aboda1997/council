from datetime import datetime, timedelta, timezone

import environ
import jwt

from core.utils.enums import TokenType


def generate_token(
    token_payload: dict[str, any], token_type: TokenType = TokenType.ACCESS_TOKEN
):
    """
    Takes some payload data and creates a JWT authentication token using it
    """
    env = environ.Env()
    audience = env('TOKEN_AUDIENCE')
    issuer = env('TOKEN_ISSUER')
    issued_at = datetime.now(tz=timezone.utc)
    expires_in = datetime.now(tz=timezone.utc) + timedelta(
        seconds=int(env('TOKEN_ACCESS_EXPIRE_IN'))
    )
    if token_type == TokenType.REFRESH_TOKEN:
        expires_in = datetime.now(tz=timezone.utc) + timedelta(
            seconds=int(env('TOKEN_REFRESH_EXPIRE_IN'))
        )
    if token_type == TokenType.RESET_TOKEN:
        expires_in = datetime.now(tz=timezone.utc) + timedelta(
            seconds=int(env('TOKEN_RESET_EXPIRE_IN'))
        )
    token_type = "ACCESS" if (token_type == TokenType.ACCESS_TOKEN) else "REFRESH"
    alogrithm = env('TOKEN_ALGORITHM')
    private_key = env('TOKEN_PRIVATE_KEY').replace('\\n', '\n')
    sign_options = {
        "aud": audience,
        "iss": issuer,
        "iat": issued_at,
        "exp": expires_in,
        "type": token_type,
    }
    token_payload = {**sign_options, **token_payload}
    return jwt.encode(token_payload, private_key, alogrithm)


def decode_token(token: str):
    """
    Takes an authentication token and decodes its data if it's valid.
    (Invalid Tokens will throw an exception, this must be handled where it's imported)
    """
    env = environ.Env()
    alogrithm = env('TOKEN_ALGORITHM')
    public_key = env('TOKEN_PUBLIC_KEY').replace('\\n', '\n')
    return jwt.decode(token, public_key, alogrithm, audience=env('TOKEN_AUDIENCE'))
