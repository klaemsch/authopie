from fastapi.responses import Response

from .. import config


def set_cookie(response: Response, key: str, value: str) -> None:
    response.set_cookie(
        key=key,
        value=value,
        samesite=config.COOKIE_SAMESITE,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        domain=config.COOKIE_DOMAIN,
        max_age=config.COOKIE_MAX_AGE
    )
