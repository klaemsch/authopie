from fastapi.param_functions import Form
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

PASSWORD_REGEX = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$ %^&*-]).{8,}$"


class MyOAuth2PasswordRequestForm:

    def __init__(
        self,
        grant_type: str = Form(..., regex="password"),
        username: EmailStr = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
        client_id: str | None = Form(None),
        client_secret: str | None = Form(None),
    ):
        self.grant_type = grant_type
        self.username = username
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class OAuth2RefreshRequestForm:

    def __init__(
        self,
        grant_type: str = Form(..., regex="refresh_token"),
        refresh_token: str = Form(...)
    ):
        self.grant_type = grant_type
        self.refresh_token = refresh_token


# TODO
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scheme_name='test',
    scopes={'a': 'b'},
    description='testtest'
)
