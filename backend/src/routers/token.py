from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, logger, schemas
from ..dependencies import database
from ..dependencies.security import (MyOAuth2PasswordRequestForm,
                                     OAuth2RefreshRequestForm)
from ..exceptions import IncorrectCredentialsException

router = APIRouter(
    prefix='/token',
    tags=['token'],
)


@router.post('', response_model=schemas.TokenPair)
async def login_for_token(
    form_data: MyOAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get)
) -> schemas.TokenPair:
    """
    Endpoint to retrieve the first token (JWT + refresh_token)
    auth with username and password
    Success: returns TokenPair (JWT/access_token + refresh_token)
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

    # return new token pair (access_token/refresh_token)
    return crud.create_token_pair(user, db)


@router.post('/refresh')
async def refresh_token(
    form_data: OAuth2RefreshRequestForm = Depends(),
    db: Session = Depends(database.get)
) -> schemas.TokenPair:
    """
    Endpoint to receive a new access_token by giving a correct refresh_token
    """

    # check if given refresh_token is in db and valid, raises 401 Unauthorized
    token = crud.validate_refresh_token(form_data.refresh_token, db)

    # return new token pair (access_token/refresh_token)
    return crud.create_token_pair(token.user, db)
