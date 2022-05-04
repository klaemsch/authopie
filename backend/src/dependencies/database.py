"""
SQLAlchemy configuration,
Mixin for creating database elements,
get connection to database
"""

from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.sql import select

from .. import config, schemas, logger
from ..exceptions import TypeException

# Docs: https://fastapi.tiangolo.com/tutorial/sql-databases/

SQLALCHEMY_DATABASE_URL = f'sqlite:///{config.DB_PATH}'

# Connect to DB by creating engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Pool of Sessions the API can use/create (used in depend in main.py)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DBMixin:

    @classmethod
    def create(
        cls,
        schema: schemas.BaseModel,
        db: Session
    ) -> schemas.BaseModel:

        # check for correct schema (only data schema)
        if not issubclass(schema.__class__, schemas.BaseModel):
            raise TypeException(schema, schemas.BaseModel)

        try:
            try:
                # create db model
                db_model = cls(**schema.dict())
            except TypeError:
                # catch custom __init__ -> forward model
                db_model = cls(schema)
            # add db model to local db instance
            db.add(db_model)
            # commit all added models to db
            db.commit()
            # refresh local model
            db.refresh(db_model)
            # create schema from db model
            return schema.__class__.from_orm(db_model)
        except sqlalchemy.exc.SQLAlchemyError as exc:
            logger.warning('DB Create thrown SQLAlchemyError')
            # TODO except SQLAlchemy
            raise exc
        except Exception as exc:
            raise exc

    @classmethod
    def get_all(
        cls,
        db: Session
    ) -> 'Base':

        stmt = select(cls)
        return db.execute(stmt).scalars().all()


# Base for Table Abstraction in models.py
Base = declarative_base()


def get() -> Session:
    """ create new database session """
    # Make Instance from SessionManager (create Session)
    db = SessionLocal()
    try:
        yield db  # return db-session
    finally:
        db.close()
