""" GET user, POST user, PUT user, DELETE user """

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import database
from ..util import auth, security
from ..util.constants import Scopes, Username

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('', response_model=schemas.UserOut)
async def get_user(
    username: Username,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get),
) -> schemas.UserOut:
    """
    searches db for user with given username
    success: returns user model
    failure: raises 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    # validates JWT + checks if user in token sub exists
    auth.authenticate_user(token_str, db)

    return crud.get_user(username, db)


@router.post(
    '',
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: schemas.UserIn,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    checks db for user with given username and then creates user in db
    Success: create user and return it (201 Created)
    user already exists: raise 409 Conflict
    AuthN Failure: 401 Unauthorized
    AuthZ Failure: 403 Forbidden
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_USERS, db)

    return crud.create_user(user, db)


@router.put('', response_model=schemas.UserOut)
async def update_user(
    username: Username,
    user: schemas.UserInUpdate,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    Update data of existing user
    success: data updated, return user
    user already exists: raise 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_USERS, db)

    return crud.update_user(username, user, db)


@router.delete('', response_model=schemas.UserOut)
async def delete_user(
    username: Username,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    searches db for user with given name and deletes it
    success: user deleted and returned
    failure: raise 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_USERS, db)

    return crud.delete_user(username, db)
