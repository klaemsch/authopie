from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

from ..dependencies.security import oauth2_access_scheme
from .. import config

router = APIRouter(
    tags=['docs'],
)


def secure_docs_wrapper():
    """
    returns secure scheme if docs should be secured
    no secured docs -> returns None
    """

    async def _secure(tokens: str = Depends(oauth2_access_scheme)):
        return tokens.access_token

    if config.SECURE_DOCS:
        return _secure
    return None


@router.get("/openapi.json")
async def get_open_api_endpoint(
    request: Request,
    token_str=Depends(secure_docs_wrapper())
) -> JSONResponse:
    """ generates and returns openapi.json for app """
    openapi = get_openapi(
        title="FastAPI",
        version=1,
        routes=request.app.routes,
        servers=config.SERVERS
    )
    # openapi["components"]["schemas"]["ValidationError"]["properties"]["loc"]["items"] = {
    #    "type": "string"}
    return JSONResponse(openapi)


@router.get("/docs")
async def get_documentation(
    token_str=Depends(secure_docs_wrapper())
) -> HTMLResponse:
    """ generates swagger docs """
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Authopie docs"
    )
