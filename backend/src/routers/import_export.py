import json

from fastapi.datastructures import UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.param_functions import Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session

from .. import crud, logger, models, schemas
from ..dependencies import auth, database, security
from ..dependencies.constants import Scopes

router = APIRouter()


@router.get('/export', tags=['export'])
async def export_authopie(
    export_users: bool = True,
    export_roles: bool = True,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
):
    """
    endpoint for exporting settings, users and roles
    """

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.GOD, db)

    export = dict()

    if export_users:
        # export users from db into expo
        export['users'] = jsonable_encoder(crud.get_all_users(db))

    if export_roles:
        # export roles from db into expo
        export['roles'] = jsonable_encoder(crud.get_all_roles(db))

    return JSONResponse(export)


@router.post('/import', tags=['import'])
async def import_authopie(
    file: UploadFile,
    import_users: bool = True,
    import_roles: bool = True,
    token_str: str = Depends(security.oauth2_scheme),
    db: Session = Depends(database.get)
):
    """
    endpoint for importing settings, users and roles
    """

    contents = await file.read()

    impo = json.loads(contents)

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.GOD, db)

    if import_roles or import_users:
        from ..dependencies.database import Base, engine

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    if import_roles:
        # import roles from impo into db
        for role in impo['roles']:
            # import role from dict
            r = schemas.RoleInDB.parse_obj(role)

            # create role in db
            models.Role.create(r, db)

        logger.debug('Roles successfully imported')

    if import_users:
        # import users from impo into db
        for user in impo['users']:

            # import user from dict
            u = schemas.UserInDB.parse_obj(user)

            # if roles shouldnt be imported, delete them from schema
            if not import_roles:
                u.roles = None

            # create user in db
            models.User.create(u, db)

        logger.debug('Users successfully imported')

    resp = dict(
        users=str(import_users),
        roles=str(import_roles),
    )

    return JSONResponse(resp)
