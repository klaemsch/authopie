from fastapi.requests import Request
from ..exceptions import TokenValidationFailedException
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from ..utils.constants import Username, Password
from fastapi.param_functions import Form


class LoginRequestForm:
    """
    Implements HTML-Form for login.
    user sends username and password along side the grant_type password
    Not quite OAuth2 conform
    TODO: dicsuss grant_type
    """

    def __init__(
        self,
        # grant_type: str = Form(..., regex="password"),
        username: Username = Form(...),
        password: Password = Form(...)
    ):
        # self.grant_type = grant_type
        self.username = username
        self.password = password


class RefreshRequestForm:
    """
    TODO useful??
    Not quite OAuth2 conform
    """

    def __init__(
        self,
        grant_type: str = Form(..., regex="refresh_token"),
        refresh_token: str = Form(...)
    ):
        self.grant_type = grant_type
        self.refresh_token = refresh_token


class OAuth2PasswordBearerWithCookie(OAuth2):
    """ This makes this funny swagger pop up for auth """

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
    description='testtest'
)
