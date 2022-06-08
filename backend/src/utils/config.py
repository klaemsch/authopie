""" load config from file """

import json
from os import path
from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):

    # list of valid server urls (mainly for openapi)
    SERVERS: list[dict[str, str]]

    # uvicorn start settings
    HOST = '127.0.0.1'
    PORT = 5555
    LOG_LEVEL = 'debug'

    # first user to be created (admin)
    DEFAULT_USER_USERNAME: str = Field(env='ADMIN_USERNAME')
    DEFAULT_USER_PASSWORD: str = Field(env='ADMIN_PASSWORD')

    # first role to be created (admin)
    DEFAULT_ROLE_NAME: str = 'authopie-admin'

    # path where database gets saved
    DB_PATH: Path = './auth.db'

    # JWT lifetime in minutes
    TOKEN_LIFETIME: int = 5

    # refresh token lifetime in days
    REFRESH_TOKEN_LIFETIME: int = 7

    # key pair lifetime in years
    KEY_PAIR_LIFETIME: int = 10

    # audience setting of JWT
    AUD: str = 'Authopie'

    # CORS Settins
    ORIGINS: list[str] = ['http://localhost:3000']
    ALLOWED_HEADERS: list[str] = ['Cookies']

    # root path for proxy
    ROOT_PATH: str = '/auth'

    # TODO for TESTING
    COOKIE_SAMESITE: str = 'None'
    COOKIE_SECURE: bool = True
    COOKIE_HTTPONLY: bool = True
    COOKIE_MAX_AGE: int = 30
    COOKIE_DOMAIN: str = '/'
    COOKIE_PATH: str = '/'

    # turn password regex on
    # -> min 8 digits
    # -> at least one upper case
    # -> at least one lower case
    # -> at least one special character
    # -> at least one number
    PASSWORD_REGEX: bool = False

    # if true username has to be an email -> will be enforced
    USERNAME_IS_EMAIL: bool = True

    # wether config should be behind auth or not
    SECURE_DOCS: bool = True


def load_config():
    if not path.exists('./config.json'):
        return Settings()
    with open('./config.json', 'r') as fh:
        data = json.load(fh)
    return Settings.parse_obj(data)
