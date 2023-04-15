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
        # if token not found -> 401 Unauthorized
        if token_str is None:
            logger.warn('No token found in request')
            raise TokenValidationFailedException
        # split str at whitespace (Bearer TOKEN)
        scheme, _, token_str = token_str.partition(' ')
        # if wrong schema -> 401 Unauthorized
        if not scheme == 'Bearer':
            logger.warn('Token has wrong schema')
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
    """
    Is used as Injection/FastAPI Depends to extract access token from requests
    This also makes this funny swagger pop up for auth
    """

    def __init__(self):
        flows = OAuthFlowsModel(
            password={"tokenUrl": 'token'})
        super().__init__(
            flows=flows,
            scheme_name='OAuth2AccessCookieBearer',
            description='Access Token Cookie or Bearer'
        )

    async def __call__(self, request: Request) -> str:
        # get access token from request (Cookie or Header)
        return get_token_from_request(request, 'access_token')


class OAuth2RefreshCookieBearer:
    """
    Is used as Injection/FastAPI Depends to extract refresh token from requests
    """

    async def __call__(self, request: Request) -> str:
        # get refresh token from request (Cookie or Header)
        return get_token_from_request(request, 'refresh_token')
