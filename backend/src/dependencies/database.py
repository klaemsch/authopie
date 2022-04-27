from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from ..config import config
from .. import schemas

# Docs: https://fastapi.tiangolo.com/tutorial/sql-databases/

SQLALCHEMY_DATABASE_URL = f'sqlite:///{config.DB_PATH}'

# Connect to DB by creating engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Pool of Sessions the API can use/create (used in depend in main.py)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class CustomBase:

    @classmethod
    def create(cls, schema: schemas.BaseModel, db: Session):

        # check for correct model (only data model)
        if not issubclass(schema.__class__, schemas.BaseModel):
            raise Exception('Thats not a Data Model')

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
        except Exception as exc:
            # TODO except SQLAlchemy
            raise exc


# Base for Table Abstraction in models.py
Base = declarative_base(cls=CustomBase)


def get() -> Session:
    """ create new database session """
    # Make Instance from SessionManager (create Session)
    db = SessionLocal()
    try:
        yield db  # return db-session
    finally:
        db.close()
