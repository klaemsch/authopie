from datetime import datetime
from typing import Literal
from uuid import uuid4

from fastapi import Form, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel as BM
from pydantic import EmailStr, Field, validator


class BaseModel(BM):

    class Config:
        orm_mode = True


class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    redirect_uris: list[str]

    def verify_redirect_uri(self, redirect_uri: str):
        # TODO allow wildcard
        if redirect_uri not in self.redirect_uris:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='invalid redirect_uri for client'
            )


class User(BaseModel):
    """Database Model of User"""
    id: str | None = Field(default_factory=lambda: str(uuid4()))
    email: str
    display_name: str | None = None
    credential_id: bytes
    credential_public_key: bytes


class AuthorizationCode(BaseModel):
    id: str | None = Field(default_factory=lambda: str(uuid4()))
    code: str
    expires: datetime
    nonce: str
    redirect_uri: str
    scope: str
    user_id: str
    client_id: str


class AuthenticationRequestParams(BaseModel):
    """https://openid.net/specs/openid-connect-core-1_0.html#ImplicitAuthRequest"""
    client_id: str
    redirect_uri: str
    scope: str  # TODO implement https://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims
    response_type: str
    # optional, not recommended, if response mode would be the default for specified response type
    response_mode: str | None
    state: str
    nonce: str

    @validator('response_type')
    def validate_response_type(cls, v: str):
        requested_response_types = v.split()
        for rt in requested_response_types:
            if rt not in ['none', 'code', 'id_token', 'token']:
                raise ValueError('invalid response_type')
        return v

    def has_response_type_none(self):
        return 'none' in self.response_type.split()

    def has_response_type_code(self):
        return 'code' in self.response_type.split()

    def has_response_type_id_token(self):
        return 'id_token' in self.response_type.split()

    def has_response_type_token(self):
        return 'token' in self.response_type.split()


class AuthenticationResponseParams(BaseModel):
    redirect_uri: str

    # recommended
    state: str | None = None

    # implicit flow
    access_token: str | None = None
    token_type: str | None = None
    id_token: str | None = None
    expires_in: int | None = None

    # code flow
    code: str | None = None

    def gen_url(self) -> str:

        # add state to redirect uri as query params
        url = f'{self.redirect_uri}?'

        # add all other params to redirect uri as query params
        for key, value in self.dict(exclude={'redirect_uri'}, exclude_none=True).items():
            url += f'&{key}={value}'

        return url


class TokenRequestParams(BaseModel):
    grant_type: Literal['authorization_code'] = Form()
    code: str = Form()
    redirect_uri: str = Form()
    client_id: str = Form()  # TODO
    client_secret: str | None = Form(None)  # TODO


class UserRegisterRequestParams(BaseModel):
    email: EmailStr
    displayName: str | None = None
    rememberMe: bool = True


class UserSignInRequestParams(BaseModel):
    email: EmailStr


