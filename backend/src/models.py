from datetime import datetime, timedelta
import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Session
from sqlalchemy.types import CHAR, TypeDecorator
from sqlalchemy.sql import select
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.sqltypes import DateTime, Integer, String

from . import schemas
from .dependencies.database import Base, SessionLocal

# TODO
db = SessionLocal()


class GUID(TypeDecorator):
    # https://gist.github.com/gmolveau/7caeeefe637679005a7bb9ae1b5e421e
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Role(Base):
    __tablename__ = "role"

    id = Column(GUID, primary_key=True, index=True, nullable=False)
    name = Column(String, index=True, nullable=False)
    scopes = Column(String)

    # define a relationship between user and role via table user_role
    users = relationship('User', secondary='user_role', back_populates='roles')

    @classmethod
    def get_by_name(cls, name: str, db: Session) -> 'Role':

        # find user by username
        stmt = select(cls).where(cls.name == name)
        return db.execute(stmt).scalars().first()

    def __str__(self):
        return str(self.__dict__)


class User(Base):
    __tablename__ = "user"

    id = Column(GUID, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # define a relationship between user and role via table user_role
    roles = relationship('Role', secondary='user_role', back_populates='users')

    @classmethod
    def create(cls, user: schemas.UserInDB, db: Session) -> schemas.UserInDB:
        """
        creates db user with given user schema
        returns user schema from db TODO necessary???
        """

        if not isinstance(user, schemas.UserInDB):
            raise Exception('Thats not a UserInDB')

        # create user roles objects
        for role in user.roles:
            db_user_role = UserRole(user_id=user.id, role_id=role.id)
            db.add(db_user_role)

        # create user object through __init__
        db_user = cls(**user.dict(exclude={'roles'}))
        db.add(db_user)

        db.commit()
        db.refresh(db_user)
        return schemas.UserInDB.from_orm(db_user)

    @classmethod
    def get_by_username(cls, username: str, db: Session) -> 'User':

        # find user by username
        stmt = select(cls).where(cls.username == username)
        return db.execute(stmt).scalars().first()

    def __str__(self):
        return str(self.__dict__)


class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(
        GUID, ForeignKey("user.id"),
        nullable=False,
        primary_key=True
    )
    role_id = Column(
        GUID, ForeignKey("role.id"),
        nullable=False,
        primary_key=True
    )


class RefreshToken(Base):
    __tablename__ = "refresh_token"

    token = Column(GUID, primary_key=True, index=True, nullable=False)
    user_id = Column(GUID, ForeignKey("user.id"), nullable=False)
    exp = Column(Integer)

    user = relationship("User", foreign_keys=[user_id])

    def __init__(self, refresh_token: schemas.RefreshToken):
        """
        creates new refresh_token object for database
        """
        self.token = refresh_token.token
        self.user_id = refresh_token.user.id
        self.exp = refresh_token.exp

    @classmethod
    def get_by_token(cls, token: str, db: Session) -> 'RefreshToken':

        # find user by username
        stmt = select(cls).where(cls.token == token)
        return db.execute(stmt).scalars().first()

    def __str__(self):
        return str(self.__dict__)


class KeyPair(Base):
    __tablename__ = "key_pair"

    # Key ID
    kid = Column(String, primary_key=True, index=True, nullable=False)
    # public key
    public_key = Column(String, nullable=False)
    # public key
    private_key = Column(String, nullable=False)
    # expire date
    exp = Column(String, nullable=False)
    # added
    added_at = Column(DateTime, nullable=False)

    @classmethod
    def get_by_kid(cls, kid: str, db: Session) -> 'KeyPair':

        # find key pair by kid
        stmt = select(cls).where(cls.kid == kid)
        return db.execute(stmt).scalars().first()

    @classmethod
    def get_valid(cls, db: Session) -> list['KeyPair']:

        # find key pair by kid
        stmt = select(cls).where(cls.exp > datetime.utcnow())
        return db.execute(stmt).scalars().all()

    def __str__(self):
        return str(self.__dict__)
