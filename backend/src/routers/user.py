from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.orm import Session

from .. import schemas, crud
from ..dependencies import database, security

router = APIRouter(
    prefix='/user',
    tags=['user'],
)


@router.get('', response_model=schemas.UserOut)
async def get_user(
    username: EmailStr,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get),
) -> schemas.UserOut:
    """
    searches db for user with given username
    success: returns user model
    failure: raises 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    # TODO AUTH

    return crud.get_user(username, db)


@router.post(
    '',
    response_model=schemas.UserOut,
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: schemas.UserIn,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    checks db for user with given username and then creates user in db
    Success: create user and return it (201 Created)
    user already exists: raise 409 Conflict
    Auth Failure: 401 Unauthorized
    """

    # TODO AUTH

    return crud.create_user(user, db)


@router.put('', response_model=schemas.UserOut)
async def update_user(
    username: EmailStr,
    user: schemas.UserInUpdate,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    Update data of existing user
    success: data updated, return user
    user already exists: raise 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    # TODO AUTH

    return crud.update_user(username, user, db)


@router.delete('', response_model=schemas.UserOut)
async def delete_user(
    username: EmailStr,
    token: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.UserOut:
    """
    searches db for user with given name and deletes it
    success: user deleted and returned
    failure: raise 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    # TODO AUTH

    return crud.delete_user(username, db)
