import uuid
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import delete, select

from .. import models, schemas
from ..config import config
from ..exceptions import (EntityDoesNotExistException,
                          IncorrectCredentialsException)


def get_refresh_token(
    token_str: str,
    db: Session
) -> schemas.RefreshToken:
    """
    searches db for token with given token string
    success: returns token model
    failure: raises 404 Not Found
    """

    token = models.RefreshToken.get_by_token(token_str, db)

    # check if any entries were found
    if token is None:
        # no db entries found -> return empty array (200 OK)
        raise EntityDoesNotExistException('RefreshToken')

    return schemas.RefreshToken.from_orm(token)


def calculate_refresh_token_exp():
    """
    returns time when the refresh token expires as integer epoch timestamp
    """
    now = datetime.utcnow()
    expires_in = timedelta(seconds=10)  # days=config.REFRESH_TOKEN_LIFETIME
    epoch = datetime(1900, 1, 1)
    return (now+expires_in-epoch).total_seconds()


def create_refresh_token(
    user: schemas.UserInDB,
    db: Session
) -> schemas.RefreshToken:
    """
    takes a user model and inserts a new refresh token into db
    """

    # generate pseudo random refresh token string
    token_str = uuid.uuid4()

    # calculate expiration time of refresh token
    exp = calculate_refresh_token_exp()

    # generate refresh token schema
    refresh_token = schemas.RefreshToken(token=token_str, user=user, exp=exp)

    return models.RefreshToken.create(refresh_token, db)


def delete_refresh_token(
    token_str: str,
    db: Session
) -> schemas.RefreshToken:

    # try to get role that shall be deleted
    # raises 404 Not Found if no role was found
    token = get_refresh_token(token_str, db)

    # create delete query
    stmt = delete(models.RefreshToken).where(
        models.RefreshToken.token == token_str)

    # execute update query locally
    db.execute(stmt)
    # commit local changes to database
    db.commit()

    return schemas.RefreshToken.from_orm(token)


def validate_refresh_token(
    token_str: str,
    db: Session
) -> schemas.RefreshToken:

    # validate token is in db and valid
    try:
        token = get_refresh_token(token_str, db)
        now = datetime.utcnow()
        epoch = datetime(1900, 1, 1)
        if (now-epoch).total_seconds() > token.exp:
            print('EXP ' + str(token.exp - (now-epoch).total_seconds()))
            # refresh token expired -> delete + raise 401 Unauthorized
            delete_refresh_token(token.token, db)
            raise IncorrectCredentialsException
        print('NOT EXP ' + str(token.exp - (now-epoch).total_seconds()))
        return token
    except EntityDoesNotExistException:
        raise IncorrectCredentialsException
