from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select, update

from .. import logger, models, schemas
from ..dependencies import pwdhash
from ..exceptions import (EntityAlreadyExistsException,
                          EntityDoesNotExistException,
                          IncorrectCredentialsException)
from .role import get_role


def get_user(username: str, db: Session) -> schemas.UserInDB:

    # find user by username
    user: models.User = models.User.get_by_username(username, db)

    # check if any entries were found
    if user is None:
        # no db entries found -> raise 404 Not Found
        raise EntityDoesNotExistException('User')

    return schemas.UserInDB.from_orm(user)


def create_user(user: schemas.UserIn, db: Session) -> schemas.UserInDB:

    # check if user already exists
    # TODO this is really clunky
    # maybe get_user with option not to throw exception and instead return None
    try:
        get_user(user.username, db)
        raise EntityAlreadyExistsException('User')
    except EntityDoesNotExistException:
        pass

    # list for role models
    roles = []

    # check if all given roles exist (raises 404 Not Found)
    for role_name in user.roles:
        role = get_role(role_name, db)
        roles.append(role)

    # create password key
    hpwd = pwdhash.get_password_hash(user.password)

    # create User schema
    new_user = schemas.UserInDB(
        username=user.username,
        hashed_password=hpwd,
        roles=roles
    )

    return models.User.create(new_user, db)


def update_user(
    username: str,
    user_update: schemas.UserInUpdate,
    db: Session
) -> schemas.UserInDB:

    # check if user exists, raises 404 Not Found if ID invalid
    db_user = models.User.get_by_username(username, db)

    if db_user is None:
        # user not found -> raise 404 Not Found
        raise EntityDoesNotExistException('User')

    if user_update.username is not None:
        try:
            # check for user with new updated username
            get_user(user_update.username, db)
            # user with username already exists
            raise EntityAlreadyExistsException('User')
        except EntityDoesNotExistException:
            # update username in model
            db_user.username = user_update.username

    if user_update.password is not None:
        # create password key and update it in model
        db_user.hashed_password = pwdhash.get_password_hash(
            user_update.password)

    if user_update.roles is not None and len(user_update.roles) > 0:
        update_user_role(db_user, user_update.roles, db)

    # commit local changes to database
    db.commit()
    # refresh local user by pulling from database
    db.refresh(db_user)

    return schemas.UserInDB.from_orm(db_user)


def update_user_role(db_user: models.User, new_roles: list[str], db: Session):
    """
    takes a list of roles (str) and
    assigns them to given user in user_role table
    """

    # list for role models
    roles: list[schemas.RoleInDB] = []

    # check if all given roles exist (raises 404 Not Found)
    for role_name in new_roles:
        role = get_role(role_name, db)
        roles.append(role)

    # delete all user_roles for given user
    stmt = delete(models.UserRole).where(
        models.UserRole.user_id == db_user.id)
    db.execute(stmt)

    # recreate user_roles with new roles
    for role in roles:
        db_user_role = models.UserRole(
            user_id=db_user.id, role_id=role.id)
        db.add(db_user_role)


def delete_user(username: str, db: Session) -> schemas.UserInDB:

    # try to get user that shall be deleted
    # raises 404 Not Found if no user was found
    user = get_user(username, db)

    # create delete query
    stmt = delete(models.User).where(
        models.User.username == username)

    # execute update query locally
    db.execute(stmt)

    # delete entries of user in user_role
    stmt = delete(models.UserRole).where(
        models.UserRole.user_id == user.id)

    # execute update query locally
    db.execute(stmt)

    # commit local changes to database
    db.commit()

    return user


def authenticate_user(
    username: str,
    password: str,
    db: Session
) -> schemas.UserInDB:
    """
    compares given username and password to db
    - user not found: raises 404 Not Found
    - password correct: returns user schema
    - password wrong: raises 401 Unauthorized
    """

    # get user by username
    # raises 404 Not Found, if no user with given username exists in db
    user = get_user(username, db)

    if not pwdhash.verify_password(password, user.hashed_password):
        # wrong password for given username
        raise IncorrectCredentialsException

    # user found, correct password
    logger.debug(f'User {username} found. Correct Password')
    return user
