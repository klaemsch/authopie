from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from .. import schemas, crud
from ..dependencies import database, security

router = APIRouter(
    prefix='/role',
    tags=['role'],
)


@router.get('', response_model=schemas.RoleOut)
async def get_role(
    name: str,
    db: Session = Depends(database.get),
    token: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    searches db for role with given name
    success: return role
    failure: raise 404 Not Found
    """

    # TODO AUTH

    return crud.get_role(name, db)


@router.post('', response_model=schemas.RoleOut)
async def create_role(
    role: schemas.RoleIn,
    db: Session = Depends(database.get),
    token: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    checks db for role with given name and then creates role in db
    success: create role and return it
    role already exists: raise 409 Conflict
    """

    # TODO AUTH

    return crud.create_role(role, db)


@router.delete('', response_model=schemas.RoleOut)
async def delete_role(
    name: str,
    db: Session = Depends(database.get),
    token: str = Depends(security.oauth2_scheme)
) -> schemas.RoleOut:
    """
    searches db for role with given name and deletes it
    success: role deleted and returned
    failure: raise 404 Not Found
    """

    # TODO AUTH

    return crud.delete_role(name, db)
