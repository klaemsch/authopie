""" GET role, POST role, DELETE role """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import database, security
from ..utils import auth
from ..utils.constants import Scopes

router = APIRouter(
    prefix='/role',
    tags=['role'],
)


@router.get('/{name}', response_model=schemas.RoleOut)
async def get_role(
    name: str,
    db: Session = Depends(database.get),
    token_str: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    searches db for role with given name
    success: return role
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.get_role(name, db)


@router.get('', response_model=list[schemas.RoleOut])
async def get_all_roles(
    db: Session = Depends(database.get),
    token_str: str = Depends(security.oauth2_scheme)
) -> list[schemas.RoleOut]:
    """
    success: returns all roles in db
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.get_all_roles(db)


@router.post('', response_model=schemas.RoleOut)
async def create_role(
    role: schemas.RoleIn,
    db: Session = Depends(database.get),
    token_str: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    checks db for role with given name and then creates role in db
    success: create role and return it
    role already exists: raise 409 Conflict
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.create_role(role, db)


@router.put('/{name}', response_model=schemas.RoleOut)
async def update_role(
    name: str,
    role: schemas.RoleInUpdate,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
) -> schemas.RoleOut:
    """
    Update data of existing role
    success: data updated, return role
    role does not exists: raise 404 Not Found
    Auth Failure: 401 Unauthorized
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.update_role(name, role, db)


@router.delete('/{name}', response_model=schemas.RoleOut)
async def delete_role(
    name: str,
    db: Session = Depends(database.get),
    token_str: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    searches db for role with given name and deletes it
    success: role deleted and returned
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.delete_role(name, db)
