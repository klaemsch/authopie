from fastapi.requests import Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security import OAuth2
from pydantic import EmailStr
from ..exceptions import TokenValidationFailedException

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


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict[str, str] | None = None,
        description: str | None = None
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(
            password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description
        )

    async def __call__(self, request: Request) -> str | None:
        authorization: str = request.cookies.get("access_token")
        if not authorization:
            raise TokenValidationFailedException
        return authorization


# TODO
oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="token",
    scheme_name='test',
    scopes={'a': 'b'},
    description='testtest'
)
