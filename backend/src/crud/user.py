from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete

from .. import logger, models, schemas
from ..exceptions import (EntityAlreadyExistsException,
                          EntityDoesNotExistException,
                          IncorrectCredentialsException)
from ..utils import pwdhash
from ..utils.constants import Password, Username
from .role import get_role


def get_user(username: Username, db: Session) -> schemas.UserInDB:
    """
    get user from db by username
    Success: return UserInDB
    Failure (no user with username): raise EntityDoesNotExistException
    """

    # find user by username
    user: models.User = models.User.get_by_username(username, db)

    # check if any entries were found
    if user is None:
        logger.debug(f'User {username} does not exist in db!')
        # no db entries found -> raise 404 Not Found
        raise EntityDoesNotExistException('User')

    return schemas.UserInDB.from_orm(user)


def get_all_users(db: Session) -> list[schemas.UserInDB]:
    """
    get all users from db
    Success: return a list of all UserInDB
    """

    return [
        schemas.UserInDB.from_orm(user)
        for user in models.User.get_all(db)
    ]


def create_user(user: schemas.UserIn, db: Session) -> schemas.UserInDB:
    """
    create new user in db from schema UserIn (username, password, roles)
    Success: return UserInDB
    Failure (username already in db): raise EntityAlreadyExistsException
    """

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

    logger.debug(f'User {new_user.username} was successfuly created')

    return models.User.create(new_user, db)


def update_user(
    username: Username,
    user_update: schemas.UserInUpdate,
    db: Session
) -> schemas.UserInDB:
    """
    update existing user in db from UserInUpdate (username, password, roles)
    Success: return UserInDB
    Failure (username not in db): raise EntityDoesNotExistException
    """

    # check if user exists
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

    # update user role table
    if user_update.roles is not None and len(user_update.roles) > 0:
        update_user_role(db_user, user_update.roles, db)

    # commit local changes to database
    db.commit()
    # refresh local user by pulling from database
    db.refresh(db_user)

    logger.debug(f'User {db_user.username} was successfuly updated')

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


def delete_user(username: Username, db: Session) -> schemas.UserInDB:
    """
    delete existing user in db by username
    Success: return UserInDB
    Failure (username not in db): raise EntityDoesNotExistException
    """

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

    logger.debug(f'User {user.username} was successfuly deleted')

    return user


def authenticate_user(
    username: Username,
    password: Password,
    db: Session
) -> schemas.UserInDB:
    """
    compares given username and password to db
    - user not found: raises 401 Unauthorized
    - password wrong: raises 401 Unauthorized
    - password correct: returns user schema
    """

    # get user by username
    try:
        # raises 404 Not Found, if no user with given username exists in db
        user = get_user(username, db)
    except EntityDoesNotExistException:
        # wrong username -> raise 401 Unauthorized
        raise IncorrectCredentialsException

    if not pwdhash.verify_password(password, user.hashed_password):
        # wrong password for given username
        raise IncorrectCredentialsException

    # user found, correct password
    logger.debug(f'User {username} found. Correct Password')
    return user
