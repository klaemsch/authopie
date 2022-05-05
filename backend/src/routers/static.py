from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import schemas
from ..dependencies import database
from ..dependencies.security import oauth2_scheme
from ..utils import auth
from ..utils.constants import Scopes
from .role import get_all_roles
from .user import get_all_users
from .token import logout as route_logout

router = APIRouter(
    prefix='/dashboard',
    tags=['dashboard']
)

templates = Jinja2Templates(directory="src/templates")


@router.get('')
async def dashboard(
    request: Request,
    users: list[schemas.UserOut] = Depends(get_all_users),
    roles: list[schemas.RoleOut] = Depends(get_all_roles)
) -> HTMLResponse:

    data = {
        'request': request,
        'users': users,
        'roles': roles
    }

    return templates.TemplateResponse("/dashboard.html", data)


@router.get('/users')
async def get_users(
    request: Request,
    users: list[schemas.UserOut] = Depends(get_all_users)
) -> HTMLResponse:

    data = {
        'request': request,
        'users': users
    }

    return templates.TemplateResponse("/users.html", data)


@router.get('/roles')
async def get_roles(
    request: Request,
    roles: list[schemas.RoleOut] = Depends(get_all_roles)
) -> HTMLResponse:

    data = {
        'request': request,
        'roles': roles
    }

    return templates.TemplateResponse("/roles.html", data)


@router.get('/api-token')
async def api_token(
    request: Request,
    token_str: str = Depends(oauth2_scheme),
    db: Session = Depends(database.get)
) -> HTMLResponse:

    token = auth.authenticate_user(token_str, db)

    auth.authorize_user(token, Scopes.GOD, db)

    data = {
        'request': request,
        'link_to_gen': '/token/api'
    }

    return templates.TemplateResponse("/api_token.html", data)


@router.get('/login')
async def login(request: Request) -> RedirectResponse:
    """ log out and redirect user """

    data = {
        'request': request,
        'link_to_login': '/token'
    }

    return templates.TemplateResponse("/login.html", data)


@router.get('/logout')
async def logout() -> RedirectResponse:
    """ log out and redirect user """

    return await route_logout()
