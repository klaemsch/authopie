from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

from .. import models, schemas
from ..exceptions import (EntityAlreadyExistsException,
                          EntityDoesNotExistException)


def get_role(name: str, db: Session) -> schemas.RoleInDB:

    # find role by name
    role: models.Role = models.Role.get_by_name(name, db)

    if role is None:
        raise EntityDoesNotExistException('Role')

    return schemas.RoleInDB.from_orm(role)


def get_all_roles(db: Session) -> list[schemas.RoleInDB]:

    return [
        schemas.RoleInDB.from_orm(role)
        for role in models.Role.get_all(db)
    ]


def create_role(role_in: schemas.RoleIn, db: Session) -> schemas.RoleInDB:

    # search for given role name in db
    stmt = select(models.Role).where(models.Role.name == role_in.name)
    role = db.execute(stmt).scalars().first()

    if role is not None:
        # role already exists
        raise EntityAlreadyExistsException('Role')

    # create Role schema
    new_role = schemas.RoleInDB(**role_in.dict())

    return models.Role.create(new_role, db)


def delete_role(name: str, db: Session) -> schemas.RoleInDB:

    # try to get role that shall be deleted
    # raises 404 Not Found if no role was found
    role = get_role(name, db)

    # create delete query
    stmt = delete(models.Role).where(
        models.Role.name == name)

    # execute update query locally
    db.execute(stmt)

    # delete entries of role in user_role
    stmt = delete(models.UserRole).where(
        models.UserRole.role_id == role.id)

    db.execute(stmt)

    # commit local changes to database
    db.commit()

    return schemas.RoleInDB.from_orm(role)
