import json
from os import path
from pathlib import Path

from pydantic import BaseSettings


class Settings(BaseSettings):

    # uvicorn start settings
    HOST = '127.0.0.1'
    PORT = 5555
    LOG_LEVEL = 'debug'

    # first user to be created (admin)
    DEFAULT_USER_USERNAME: str = 'authopie@authopie.com'
    DEFAULT_USER_PASSWORD: str = 'authopie'

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
    BASE_URLS: list[str] = ['http://localhost:3000']


def load_config():
    if not path.exists('./config.json'):
        return Settings()
    with open('./config.json', 'r') as fh:
        data = json.load(fh)
    return Settings.parse_obj(data)


# default
config = load_config()
