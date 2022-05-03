from fastapi.params import Cookie
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from .. import crud, logger, schemas, util
from ..dependencies import auth, database, security, cookie
from ..dependencies.constants import Scopes
from ..exceptions import IncorrectCredentialsException

router = APIRouter(
    prefix='/token',
    tags=['token'],
)


@router.post('', response_model=schemas.TokenPair)
async def login_for_token(
    response: Response,
    form_data: security.MyOAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get)
) -> schemas.TokenPair:
    """
    Endpoint to retrieve the first token (access + refresh token pair)
    auth with username and password
    Success: returns TokenPair (access_token + refresh_token)
    Failure: Returns 401 Unauthorized
    """

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

    return token_pair


@router.post('/refresh')
async def refresh_token(
    response: Response,
    form_data: security.OAuth2RefreshRequestForm = Depends(),
    db: Session = Depends(database.get)
) -> schemas.TokenPair:
    """
    Endpoint to receive a new access_token by giving a correct refresh_token
    """

    # authenticate token / user with given refresh token
    user = auth.authenticate_user(form_data.refresh_token, db)

    # create new token pair (access_token/refresh_token)
    token_pair = auth.create_token_pair(user, db)

    # add cookie for access_token
    cookie.set_cookie(response, 'access_token', token_pair.access_token)

    # add cookie for refresh_token
    cookie.set_cookie(response, 'refresh_token', token_pair.refresh_token)

    return token_pair


@router.get('/api')
async def get_api_token(
    exp: int,
    sub: str,
    aud: str,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> str:

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
