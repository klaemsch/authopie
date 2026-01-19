from typing import Literal

from fastapi import APIRouter, Depends, Form, status
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from . import schemas
from ..dependencies import database

"""
from .. import clientStore, config, database, schemas, stateStore, templates
from ..stores import State
from ..util.helpers import get_user_from_request
from ..util.keys import get_valid_key_pairs
from ..util.logger import logger
from ..util.oid import create_auth_response, is_valid_client_id
"""
router = APIRouter(
    prefix='',
    tags=['oid'],
)


@router.get('/connect/authorize', response_class=HTMLResponse)
async def authorize(
    request: Request,
    params: schemas.AuthenticationRequestParams = Depends(
        schemas.AuthenticationRequestParams),
    db: Session = Depends(database.get)
):

    state = State(oidc_req_params=params)
    stateStore.add(state)

    logger.debug(f'added new state with id {state.id}')

    # check for valid client and redirect uri
    client = is_valid_client_id(params.client_id)
    client.verify_redirect_uri(params.redirect_uri)

    # if request contains user cookie -> add user to state
    user = get_user_from_request(request, db)
    if user is not None:
        state.user_id = user.id
        print(user.display_name)

    if request.url.hostname == '127.0.0.1':
        logger.warn(f"""
        You are trying to access MPAS via 127.0.0.1.
        This is not recommended, because WebAuthn will not work this way.
        You can find more information here: {config.server.base_path}/getting-started.html#debugging
        """)

    return templates.TemplateResponse('popup.html', {'request': request, 'stateId': state.id, 'user': user})


@router.get('/logout')
async def logout(
    request: Request
):

    # find user id in session and delete it
    if 'uid' in request.session:
        request.session.pop('uid')

    # redirect to referer if possible
    if 'referer' in request.headers:
        return RedirectResponse(request.headers['referer'])
    else:
        return RedirectResponse('/')


@router.post(
    '/connect/token',
    response_model=schemas.AuthenticationResponseParams,
    response_model_exclude_none=True
)
async def token(
    request: Request,
    # params: schemas.TokenRequestParams = Form(),
    grant_type: Literal['authorization_code'] = Form(),
    code: str = Form(),
    redirect_uri: str = Form(),
    client_id: str = Form(),  # TODO
    client_secret: str | None = Form(None),  # TODO
    db: Session = Depends(database.get)
):
    """
    https://openid.net/specs/openid-connect-core-1_0.html#TokenRequestValidation
    https://www.rfc-editor.org/rfc/rfc6749#section-4.1.3
    """

    # authenticate the client, if not valid raises http exception
    client = clientStore.get(client_id)

    # verify that authorization code is valid and was not used previously
    authorization_code = database.AuthorizationCode.get_by_code(db, code)
    if authorization_code is None or authorization_code.id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid code'
        )
    else:
        # delete code from db to prevent repeated usage
        database.AuthorizationCode.delete_by_id(db, authorization_code.id)

    # make sure the authorization code was issued for the client
    if authorization_code.client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='invalid client for code'
        )

    # get the user the code was issued for
    user = database.User.get_by_id(db, authorization_code.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='user the token was issued for was not found'
        )

    # verify that the redirect_uri parameter given now equals the one given with the original code request
    if redirect_uri != authorization_code.redirect_uri:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='given redirect uri did not match redirect uri from code request'
        )

    # get valid key pair for token signing
    key_pair = get_valid_key_pairs(db)[0]

    user = schemas.User(**user.dict())

    # create response data with token etc.
    auth_response = create_auth_response(
        db=db,
        user=user,
        client=client,
        key_pair=key_pair,
        redirect_uri=redirect_uri,
        response_type=['id_token', 'token'],
        scope=authorization_code.scope,
        nonce=authorization_code.nonce,
        state=None
    )

    # return generated redirect url
    return auth_response
