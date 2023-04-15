from datetime import datetime, timedelta

from fastapi.encoders import jsonable_encoder
from jose import jws, jwt
from jose.exceptions import JWSError, JWTError
from sqlalchemy.orm import Session

from .. import config, crud, logger, schemas
from ..exceptions import (ActionForbiddenException,
                          EntityDoesNotExistException,
                          TokenValidationFailedException, TypeException)
from .constants import Scopes


def calculate_token_exp(expires_in: timedelta):
    """
    returns token expiry time as integer epoch timestamp
    """
    now = datetime.utcnow()
    epoch = datetime(1900, 1, 1)
    return (now+expires_in-epoch).total_seconds()


def exp_access_token():
    """
    returns expiry time of access token
    """
    lifetime = timedelta(minutes=config.TOKEN_LIFETIME)
    return calculate_token_exp(lifetime)


def exp_refresh_token():
    """
    returns expiry time of refresh token
    """
    lifetime = timedelta(days=config.REFRESH_TOKEN_LIFETIME)
    return calculate_token_exp(lifetime)


def encode_token(
    key_pair: schemas.KeyPair,
    token: schemas.Token
) -> str:
    """
    takes a token schema and encodes it with given private key
    returns a encoded JWT string
    """

    # create payload (encode to dict)
    payload = jsonable_encoder(token, exclude=['user'])

    # save kid of signing key in jwt headers
    headers = dict(kid=key_pair.kid)

    # encode token with given private key
    return jwt.encode(
        payload,
        key_pair.private_key,
        algorithm='RS256',
        headers=headers
    )


def create_access_token(
    user: schemas.UserInDB,
    key_pair: schemas.KeyPair
) -> schemas.TokenPair:
    """
    Create access token (JWT) for given user
    - signed with given private key
    - sub = username of given user
    """

    # calculate lifetime of token (timestamp)
    exp = exp_access_token()

    # get scopes for given user
    user_scope_set = set()
    for role in user.roles:
        # get scope str for each role
        scopes_set_for_role = set(role.scopes.split(' '))
        # add new found scopes to user scope
        user_scope_set.update(scopes_set_for_role)

    # create token model
    token = schemas.Token(exp=exp, scopes=user_scope_set, sub=user.username)

    # encode token data, get access token
    access_token = encode_token(key_pair, token)

    return access_token


def create_refresh_token(
    user: schemas.UserInDB,
    key_pair: schemas.KeyPair
) -> schemas.TokenPair:
    """
    Create refresh token (JWT) for given user
    - signed with given private key
    - sub = username of given user
    """

    # calculate lifetime of token (timestamp)
    exp = exp_refresh_token()

    # create token model
    token = schemas.Token(exp=exp, sub=user.username)

    # encode token data, get refresh token
    access_token = encode_token(key_pair, token)

    return access_token


def create_token_pair(
    user: schemas.UserInDB,
    db: Session
) -> schemas.TokenPair:
    """
    gets random key pair from db and creates two tokens
    - access token (JWT), signed with private key from db
    - refresh token (JWT), signed with private key from db
    """

    key_pair = crud.get_random_valid_key_pair(db)

    access_token = create_access_token(user, key_pair)
    refresh_token = create_refresh_token(user, key_pair)

    return schemas.TokenPair(
        access_token=access_token,
        refresh_token=refresh_token
    )


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
    'require_nbf': True,
    'require_iss': True,
    'require_sub': True,
    'require_jti': True,
    'require_at_hash': False,
    'leeway': 0,
}


def validate_jwt(token: str, db: Session) -> schemas.Token:
    """
    takes JWT string and decodes it using the public RSA key
    success: returns token schema
    failure: raises 401 Unauthorized
    """

    if not isinstance(token, str):
        logger.warn('JWT validation failed - not a string')
        print(type(token))
        raise TokenValidationFailedException

    try:

        # load kid of key that signed given key
        header = jws.get_unverified_header(token)
        kid = header['kid']

        try:
            # load key pair that signed the token from db
            key_pair = crud.get_key_pair(kid, db)
        except EntityDoesNotExistException as exc:
            # the key pair the token was signed with does not exist (anymore)
            logger.warning(exc.detail)
            raise TokenValidationFailedException

        # get public key for decoding of given JWT
        public_key = key_pair.public_key

        decoded_token = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=config.AUD,
            options=options
        )
        token = schemas.Token.parse_obj(decoded_token)
        return token
    except (JWTError, JWSError) as exc:
        logger.warn(exc)
        raise TokenValidationFailedException


def authenticate_user(token_str: str, db: Session) -> schemas.Token:
    """
    Make sure the user is who he claims to be
    by checking the given JWT
    - validates JWT
    - checks if user in token.sub exists
    success: returns token
    failure: raises 401 Unauthorized
    """

    # check if given refresh_token (JWT) is valid, raises 401 Unauthorized
    token = validate_jwt(token_str, db)

    try:
        # get username from token (stored in sub) and search for it in db
        user = crud.get_user(token.sub, db)
        # assign user to token
        token.user = user
        return token
    except EntityDoesNotExistException:
        logger.warn('JWT contains a username that doesnt exist!')
        raise TokenValidationFailedException


def authorize_user(
    token: schemas.Token,
    required_scope: Scopes,
    db: Session
) -> None:
    """
    Make sure the user has permissions to
    access what he wants to access
    - checks the scopes in the given JWT against given required scope
    success: returns None
    failure: raises 403 Forbidden
    """

    # check if token is a schema
    if not isinstance(token, schemas.Token):
        raise TypeException(token, schemas.Token)

    # check if token contains the required scope
    if token.scopes not in required_scope:
        raise ActionForbiddenException(required_scope)
