from datetime import datetime, timedelta

from fastapi.encoders import jsonable_encoder
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.orm import Session

from .. import logger, schemas, crud
from ..config import config
from ..dependencies import etc
from ..exceptions import IncorrectCredentialsException


def calculate_token_exp():
    """
    returns time when the token expires as integer epoch timestamp
    """
    now = datetime.utcnow()
    expires_in = timedelta(minutes=config.TOKEN_LIFETIME)
    epoch = datetime(1900, 1, 1)
    return (now+expires_in-epoch).total_seconds()


def encode_token(
    key_pair: schemas.KeyPair,
    token: schemas.Token
) -> str:
    """
    takes a token schema and encodes it with given private key
    returns a encoded JWT string
    """

    # create payload (encode to dict)
    payload = jsonable_encoder(token)

    # encode token -> generate access_token
    return jwt.encode(payload, key_pair.private_key, algorithm='RS256')


def create_access_token(
    user: schemas.UserInDB,
    db: Session
) -> schemas.TokenPair:
    """
    Create JWT and refresh token for given user
    - access_token: JWT with claims and scopes
    - refresh_token: str to refresh access token on expiration
    """

    # calculate lifetime of token (timestamp)
    exp = calculate_token_exp()

    # get scopes for given user
    user_scope_set = set()
    for role in user.roles:
        # get scope str for each role
        scopes_set_for_role = set(role.scopes.split(' '))
        # add new found scopes to user scope
        user_scope_set.update(scopes_set_for_role)

    # create token model
    token = schemas.Token(exp=exp, scopes=user_scope_set)

    # load random valid key pair from database
    key_pair = crud.get_random_valid_key_pair(db)

    # encode token data, get access token
    access_token = encode_token(key_pair, token)

    return access_token


options = {
    'verify_signature': True,
    'verify_aud': True,
    'verify_iat': True,
    'verify_exp': True,
    'verify_nbf': True,
    'verify_iss': True,
    'verify_sub': True,
    'verify_jti': True,
    'verify_at_hash': True,
    'require_aud': True,
    'require_iat': True,
    'require_exp': True,
    'require_nbf': False,
    'require_iss': True,
    'require_sub': True,
    'require_jti': True,
    'require_at_hash': False,
    'leeway': 0,
}


def validate_access_token(token: str) -> schemas.Token:
    """
    takes JWT string and decodes it using the public RSA key
    success: returns token schema
    failure: raises 401 Unauthorized
    """

    try:
        decoded_token = jwt.decode(
            token,
            etc.load_rsa_public_key(),
            algorithms=['RS256'],
            audience=config.AUD,
            options=options
        )
        token = schemas.Token.parse_obj(decoded_token)
        logger.debug(token)
        return token
    except JWTError as exc:
        logger.warn(exc)
        raise IncorrectCredentialsException
