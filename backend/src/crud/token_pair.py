from sqlalchemy.orm import Session

from .. import schemas
from .access_token import create_access_token
from .refresh_token import create_refresh_token


def create_token_pair(
    user: schemas.UserInDB,
    db: Session
) -> schemas.TokenPair:

    access_token = create_access_token(user, db)

    refresh_token = create_refresh_token(user, db)

    # get refresh token string
    rts = refresh_token.token

    return schemas.TokenPair(
        access_token=access_token,
        refresh_token=rts
    )
