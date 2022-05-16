from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.requests import Request
from fastapi.security import OAuth2

from ..exceptions import TokenValidationFailedException
from ..utils.constants import Password, Username
from .. import logger


def get_token_from_request(request: Request, key: str) -> str:
    """
    Looks into request and extracts token from either cookie or auth header
    Success: returns token string (JWT)
    Failure: raises 401 Unauthorized
    """
    token_str: str = request.cookies.get(key)
    if token_str is None:
        # retrieve token from auth header
        token_str: str = request.headers.get("Authorization")
        # split str at whitespace (Bearer TOKEN)
        scheme, _, token_str = token_str.partition(' ')
        # if token not found or wrong schema -> 401 Unauthorized
        if token_str is None or not scheme == 'Bearer':
            logger.warn('No token found in request')
            raise TokenValidationFailedException
    # logger.debug(token_str)
    return token_str


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


class OAuth2AccessCookieBearer(OAuth2):
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

    async def __call__(self, request: Request) -> str:
        return get_token_from_request(request, 'access_token')


class OAuth2RefreshCookieBearer(OAuth2):
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

    async def __call__(self, request: Request) -> str:
        return get_token_from_request(request, 'refresh_token')


# TODO
oauth2_access_scheme = OAuth2AccessCookieBearer(
    tokenUrl="token",
    scheme_name='test',
    description='testtest'
)

oauth2_refresh_scheme = OAuth2RefreshCookieBearer(
    tokenUrl="token",
    scheme_name='test',
    description='testtest'
)
