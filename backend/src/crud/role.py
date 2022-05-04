from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

from .. import logger, models, schemas
from ..exceptions import (EntityAlreadyExistsException,
                          EntityDoesNotExistException)


def get_role(name: str, db: Session) -> schemas.RoleInDB:
    """
    get role from db by name
    Success: return RoleInDB
    Failure (no role with name): raise EntityDoesNotExistException
    """

    # find role by name
    role: models.Role = models.Role.get_by_name(name, db)

    # check if any entries were found
    if role is None:
        # no db entries found -> raise 404 Not Found
        raise EntityDoesNotExistException('Role')

    return schemas.RoleInDB.from_orm(role)


def get_all_roles(db: Session) -> list[schemas.RoleInDB]:
    """
    get all roles from db
    Success: return a list of all RoleInDB
    """

    return [
        schemas.RoleInDB.from_orm(role)
        for role in models.Role.get_all(db)
    ]


def create_role(role_in: schemas.RoleIn, db: Session) -> schemas.RoleInDB:
    """
    create new role in db from schema RoleIn (name, scopes)
    Success: return RoleInDB
    Failure (name already in db): raise EntityAlreadyExistsException
    """

    # search for given role name in db
    stmt = select(models.Role).where(models.Role.name == role_in.name)
    role = db.execute(stmt).scalars().first()

    if role is not None:
        # role already exists
        raise EntityAlreadyExistsException('Role')

    # create Role schema
    new_role = schemas.RoleInDB(**role_in.dict())

    logger.debug(f'Role {new_role.name} was successfuly created')

    return models.Role.create(new_role, db)


def delete_role(name: str, db: Session) -> schemas.RoleInDB:
    """
    delete existing role in db by name
    Success: return RoleInDB
    Failure (name not in db): raise EntityDoesNotExistException
    """

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

    logger.debug(f'Role {role.name} was successfuly deleted')

    return role
