from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import auth, database, security
from ..dependencies.constants import Scopes

router = APIRouter(
    prefix='/role',
    tags=['role'],
)


@router.get('', response_model=schemas.RoleOut)
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


@router.delete('', response_model=schemas.RoleOut)
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
