from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, crud, logger, schemas
from .dependencies import database
from .exceptions import EntityAlreadyExistsException
from .routers import (docs, import_export, jwks, key_pairs,
                      role, token, user)

app = FastAPI(
    root_path=config.ROOT_PATH,
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Settings for handling of Cross-Origin-Requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=config.ALLOWED_HEADERS,
)

app.include_router(token.router)
app.include_router(user.router)
app.include_router(role.router)
app.include_router(jwks.router)
app.include_router(key_pairs.router)
app.include_router(import_export.router)
app.include_router(docs.router)


@app.on_event("startup")
async def startup_event():

    logger.debug('StartUp event triggered')

    from .dependencies.database import Base, engine

    # Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = database.SessionLocal()

    # tries to find keys, generates them if not found
    crud.create_key_pair(db)

    # create authopie-admin role with super powers
    try:
        default_role = crud.create_role(
            schemas.RoleIn(name=config.DEFAULT_ROLE_NAME, scopes='*'),
            db
        )
        logger.debug('DEFAULT_ROLE created')
    except EntityAlreadyExistsException:
        logger.debug('DEFAULT_ROLE already present in DB')
        default_role = crud.get_role(config.DEFAULT_ROLE_NAME, db)

    # create authopie-admin user with role assigned
    try:
        user = schemas.UserIn(
            username=config.DEFAULT_USER_USERNAME,
            password=config.DEFAULT_USER_PASSWORD,
            roles=[default_role.name]
        )
        crud.create_user(user, db)
        logger.debug('DEFAULT_USER created')
    except EntityAlreadyExistsException:
        logger.debug('DEFAULT_USER already present in DB')

    db.close()
