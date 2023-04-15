""" GET key pair, POST key pair, DELETE key pair """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import database, security
from ..utils import auth
from ..utils.constants import Scopes

router = APIRouter(
    prefix='/key_pair',
    tags=['key_pair'],
)


@router.get('{kid}', response_model=schemas.KeyPairOut)
async def get_key_pair(
    kid: str,
    db: Session = Depends(database.get),
    token_str: str = Depends(security.OAuth2AccessCookieBearer())
) -> schemas.KeyPairOut:
    """
    searches db for keypair with given id
    success: return keypair
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_KEY_PAIRS, db)

    return crud.get_key_pair(kid, db)


@router.get('', response_model=list[schemas.KeyPairOut])
async def get_all_key_pairs(
    db: Session = Depends(database.get),
    token_str: str = Depends(security.OAuth2AccessCookieBearer())
) -> list[schemas.KeyPairOut]:
    """
    success: returns all key pairs in db
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_KEY_PAIRS, db)

    return crud.get_all_key_pairs(db)


@router.post('', response_model=schemas.KeyPairOut)
async def create_key_pair(
    db: Session = Depends(database.get),
    token_str: str = Depends(security.OAuth2AccessCookieBearer())
) -> schemas.KeyPairOut:
    """
    creates a new keypair
    success: returns keypair that was created
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_KEY_PAIRS, db)

    return crud.create_key_pair(db)


@router.delete('/{kid}', response_model=schemas.KeyPairOut)
async def delete_key_pair(
    kid: str,
    db: Session = Depends(database.get),
    token_str: str = Depends(security.OAuth2AccessCookieBearer())
) -> schemas.KeyPairOut:
    """
    searches db for keypair with given id and deletes it
    success: keypair deleted and returned
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_KEY_PAIRS, db)

    return crud.delete_key_pair(kid, db)
