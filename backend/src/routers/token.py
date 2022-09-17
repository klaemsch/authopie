""" GET TOKEN, UPDATE TOKEN, GET API TOKEN """

from fastapi import APIRouter, Depends
from fastapi.responses import Response, JSONResponse
from sqlalchemy.orm import Session

from ..utils import auth, cookie

from .. import crud, logger, schemas
from ..dependencies import database, security
from ..utils.constants import Scopes
from ..exceptions import IncorrectCredentialsException

router = APIRouter(
    prefix='/token',
    tags=['token'],
)


@router.post('')
async def login_for_token(
    response: Response,
    form_data: security.LoginRequestForm = Depends(),
    db: Session = Depends(database.get)
):
    """
    Endpoint to retrieve the first token (access + refresh token pair)
    auth with username and password
    Success: returns 200 OK with cookies (access_token + refresh_token)
    Failure: Returns 401 Unauthorized
    """

    print(form_data.username, form_data.password)

    # check username and password
    user = crud.authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    # wrong credentials
    if not user:
        logger.debug('Incorrect username or password...')
        raise IncorrectCredentialsException

    # create new token pair (access_token/refresh_token)
    token_pair = auth.create_token_pair(user, db)

    # add cookie for access_token
    cookie.set_cookie(response, 'access_token', token_pair.access_token)

    # add cookie for refresh_token
    cookie.set_cookie(response, 'refresh_token', token_pair.refresh_token)

    return


@router.post('/refresh')
async def refresh_token(
    response: Response,
    token_str: str = Depends(security.OAuth2RefreshCookieBearer()),
    db: Session = Depends(database.get)
):
    """
    Generate a new token pair by giving a correct refresh_token
    Success: returns 200 OK with cookies (access_token + refresh_token)
    Failure: Returns 401 Unauthorized
    """

    # authenticate token / user with given refresh token
    token = auth.authenticate_user(token_str, db)

    # create new token pair (access_token/refresh_token)
    token_pair = auth.create_token_pair(token.user, db)

    # add cookie for access_token
    cookie.set_cookie(response, 'access_token', token_pair.access_token)

    # add cookie for refresh_token
    cookie.set_cookie(response, 'refresh_token', token_pair.refresh_token)

    return


@router.get('/test')
async def test_token(
    token_str: str = Depends(security.OAuth2AccessCookieBearer()),
    db: Session = Depends(database.get)
):
    """
    Test Endpoint: Checks given tokens for validity
    Success: returns 200 OK
    AuthN Failure: Returns 401 Unauthorized
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.NONE, db)

    return JSONResponse({'detail': 'Authorization confirmed.'})


@router.get('/api')
async def get_api_token(
    exp: int,
    sub: str,
    aud: str,
    token_str: str = Depends(security.OAuth2AccessCookieBearer()),
    db: Session = Depends(database.get)
) -> str:
    """
    Generates a new API-Token (JWT)
    Success: returns API-Token (JWT) as str
    AuthN Failure: Returns 401 Unauthorized
    AuthZ Failure: Returns 403 Forbidden
    """

    # TODO discuss security aspects and possible misuses of this

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.GOD, db)

    api_token = schemas.Token(
        exp=exp,
        sub=sub,
        aud=aud
    )

    key_pair = crud.get_random_valid_key_pair(db)

    return auth.encode_token(key_pair, api_token)


@router.get('/logout')
async def logout():
    """
    log out user by deleting their cookies
    TODO: route path is currently /token/logout,
    but maybe /logout would be better
    """

    response = Response()
    cookie.delete_cookie(response, 'access_token')
    cookie.delete_cookie(response, 'refresh_token')
    return response
