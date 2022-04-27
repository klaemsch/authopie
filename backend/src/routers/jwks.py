from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from jose import jwk

from .. import schemas, crud
from ..dependencies import database

router = APIRouter(
    tags=['jwks'],
)


@router.get('/.well-known/jwks.json', response_model=schemas.JWKS)
async def get_jwks(db: Session = Depends(database.get)) -> schemas.JWKS:
    """
    public endpoint for retrieving the json web key set of this auth server
    """

    jwks = []

    # get key pairs from database
    key_pair_list: list[schemas.KeyPair] = crud.get_valid_key_pairs(db)

    # iterate over key pairs and construct jwk for every pair
    for key_pair in key_pair_list:

        key_dict = jwk.construct(key_pair.public_key, 'RS256').to_dict()
        # set key id (kid) and create schema
        key = schemas.JWK(**key_dict, kid=key_pair.kid)
        jwks.append(key)

    return schemas.JWKS(keys=jwks)
