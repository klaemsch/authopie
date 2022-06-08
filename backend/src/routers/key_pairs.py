""" GET key pair, POST key pair, DELETE key pair """
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..dependencies import database, security
from ..utils import auth
from ..utils.constants import Scopes

router = APIRouter(
    prefix='/key_pairs',
    tags=['key_pairs'],
)


@router.get('', response_model=list[schemas.KeyPairOut])
async def get_all_key_pairs(
    db: Session = Depends(database.get),
    token_str: str = Depends(security.oauth2_access_scheme)
) -> list[schemas.KeyPairOut]:
    """
    success: returns all key pairs in db
    failure: raise 404 Not Found
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.MANAGE_ROLES, db)

    return crud.get_all_key_pairs(db)
