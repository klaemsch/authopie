import random
import secrets
from datetime import datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.orm import Session

from .. import config, logger, models, schemas
from ..exceptions import EntityDoesNotExistException


def get_key_pair(kid: str, db: Session) -> schemas.KeyPair:
    """
    get key pair from db by key id
    Success: return KeyPair
    Failure (no key pair with kid): raise EntityDoesNotExistException
    """

    # find key_pair by kid
    key_pair: models.KeyPair = models.KeyPair.get_by_kid(kid, db)

    if key_pair is None:
        raise EntityDoesNotExistException('KeyPair')

    return schemas.KeyPair.from_orm(key_pair)


def get_all_key_pairs(db: Session) -> list[schemas.KeyPair]:
    """
    get all key pairs from db (valid AND invalid)
    Success: return a list of all KeyPairs
    """

    return [
        schemas.KeyPair.from_orm(key_pair)
        for key_pair in models.KeyPair.get_all(db)
    ]


def get_valid_key_pairs(db: Session) -> list[schemas.KeyPair]:
    """
    get all valid key pairs from db
    Success: return a list of all KeyPair
    """

    return [
        schemas.KeyPair.from_orm(key_pair)
        for key_pair in models.KeyPair.get_valid(db)
    ]


def get_random_valid_key_pair(db: Session) -> schemas.KeyPair:
    """
    get a random valid key pair from db
    Success: returns a random KeyPair
    (if no key pair exists -> create a new one and return it)
    """

    keys = get_valid_key_pairs(db)
    if len(keys) == 0:
        logger.debug('No KeyPair found. Creating a new one...')
        # if no key pair exists -> create key pair and return it
        return create_key_pair(db)
    return random.choice(keys)


def calculate_token_exp():
    """
    returns time when the token expires as integer epoch timestamp
    """
    now = datetime.utcnow()
    expires_in = timedelta(days=config.KEY_PAIR_LIFETIME*365)
    epoch = datetime(1900, 1, 1)
    return (now+expires_in-epoch).total_seconds()


def create_key_pair(db: Session) -> schemas.KeyPair:
    """
    Generates a new rsa key pair and saves it to db
    Success: returns a new KeyPair
    """

    # seach if there are valid key pairs in db
    valid_key_pairs = get_valid_key_pairs(db)

    # if there are -> return first result
    if len(valid_key_pairs) > 0:
        return valid_key_pairs[0]

    # else start generating a new key pair

    PUBLIC_EXPONENT = 65537
    KEY_SIZE = 2048

    # generate private/secret key
    private_key = rsa.generate_private_key(
        public_exponent=PUBLIC_EXPONENT,
        key_size=KEY_SIZE,
    )

    # save private/secret key as PEM
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # generate public key
    public_key = private_key.public_key()

    # save public key as PEM
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    # calculate expire date
    exp = datetime.utcnow() + timedelta(days=config.KEY_PAIR_LIFETIME*365)

    # new key pair schema with kid and expire date
    key_pair = schemas.KeyPair(
        kid=secrets.token_urlsafe(),
        private_key=private_key_pem,
        public_key=public_key_pem,
        exp=exp
    )

    # save new key pair to db
    key_pair: schemas.KeyPair = models.KeyPair.create(key_pair, db)

    logger.debug(f'KeyPair {key_pair.kid} was successfuly created')

    return key_pair
