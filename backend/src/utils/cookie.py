""" set cookies in response to client """

from fastapi.responses import Response

from .. import config


def set_cookie(response: Response, key: str, value: str) -> Response:
    """ set cookies in given response """

    # TODO: should all values be set by config?
    response.set_cookie(
        key=key,
        value=value,
        path=config.COOKIE_PATH,
        samesite=config.COOKIE_SAMESITE,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        domain=config.COOKIE_DOMAIN,
        max_age=config.COOKIE_MAX_AGE
    )
    return response


def delete_cookie(response: Response, key: str) -> Response:
    response.delete_cookie(
        key,
        path=config.COOKIE_PATH,
        domain=config.COOKIE_DOMAIN,
        secure=config.COOKIE_SECURE,
        httponly=config.COOKIE_HTTPONLY,
        samesite=config.COOKIE_SAMESITE
    )
