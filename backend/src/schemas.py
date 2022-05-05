from unicodedata import name
import uuid
from datetime import datetime
from time import time

from pydantic import BaseModel, Extra, Field, root_validator, validator

from . import config
from .utils.constants import Username, Password


class HashableBaseModel(BaseModel):
    # https://stackoverflow.com/questions/63721614/unhashable-type-in-fastapi-request
    def __hash__(self):  # make hashable BaseModel subclass
        return hash((type(self),) + tuple(self.__dict__.values()))


""" Role """


class RoleBase(HashableBaseModel):
    name: str
    scopes: str | None = ''

    @validator('scopes')
    def every_scope_only_once(cls, v):
        scope_list = v.split(' ')
        check_list = list(set(scope_list))
        if [scope_list].sort() == check_list.sort():
            return v
        raise ValueError(
            'scopes has to be a string with every scope appearing only once')


class RoleIn(RoleBase):
    pass


class RoleInUpdate(RoleIn):
    name: str | None
    scopes: str | None

    @root_validator(skip_on_failure=True)
    def check_for_no_data(cls, values):
        name_check = values['name'] is None
        scope_check = values['scopes'] is None
        if all([name_check, scope_check]):
            raise ValueError('No data received')
        return values


class RoleOut(RoleBase):
    pass


class RoleInDB(RoleBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)

    class Config:
        orm_mode = True


""" USER """


class UserBase(HashableBaseModel):
    username: Username


class UserIn(UserBase):
    username: Username
    password: Password
    roles: list[str] | None = []


class UserInUpdate(UserIn):
    username: Username | None
    password: Password | None

    @root_validator(skip_on_failure=True)
    def check_for_no_data(cls, values):
        username_check = values['username'] is None
        password_check = values['password'] is None
        roles_check = len(values['roles']) == 0
        if all([username_check, password_check, roles_check]):
            raise ValueError('No data received')
        return values


class UserOut(UserBase):
    roles: list[RoleBase] | None = []


class UserInDB(UserBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    hashed_password: str
    roles: list[RoleInDB] | None = []

    class Config:
        orm_mode = True


""" INTERN DB MODELS """


class RefreshToken(HashableBaseModel):
    token: uuid.UUID
    user: UserInDB
    exp: int

    class Config:
        orm_mode = True


class KeyPair(HashableBaseModel):
    kid: str                        # Key ID
    public_key: str                 # PEM encoded public RSA key
    private_key: str                # PEM encoded private RSA key
    exp: datetime                   # exprire date
    added_at: datetime | None    # datetime of model creation

    @validator('added_at', pre=True, always=True)
    def add_added_at(cls, v):
        # always add the current time, prevent misuse
        return datetime.utcnow()

    class Config:
        orm_mode = True


""" Pure Response Models """


class TokenPair(HashableBaseModel):
    access_token: str  # string encoded jwt
    refresh_token: str  # string encoded jwt
    token_type: str = 'Bearer'


class Token(HashableBaseModel):
    # issuer
    iss: str | None = 'authopie'
    # subject (Auftraggeber)
    sub: str
    # audience (Empfänger)
    aud: str | None = config.AUD
    # expiration time
    exp: int
    # not before TODO
    nbf: int | None = 0
    # issued at (current timestamp in seconds)
    iat: int | None = int(time())
    # jwt id
    jti: uuid.UUID | None = Field(default_factory=uuid.uuid4)
    # areas the user has access to
    scopes: list[str] = []

    class Config:
        extra = Extra.allow  # allows us to append extra data


class JWK(HashableBaseModel):
    kid: str            # Key ID
    kty: str = 'RSA'    # Key Type / key family
    alg: str = 'RS256'  # Algorithm
    use: str = 'sig'    # sig (sign) or enc (encrypt)
    n: str              # modulus
    e: str = 'AQAB'     # public exponent

    # TODO: for now optional
    x5c: str | None  # x.509 certificate chain
    x5t: str | None  # sha-1 thumbprint of the x.509 cert


class JWKS(HashableBaseModel):
    keys: list[JWK]
