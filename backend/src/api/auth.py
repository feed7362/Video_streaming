from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from ..infrastructure.keycloak_client import get_current_user, require_role

router_auth = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


@router_auth.get("/admin")
async def admin_panel(user=Depends(require_role("admin"))):
    return {"msg": f"Hello Admin {user.username}"}


@router_auth.get("/current_user")
async def user_panel(user=Depends(get_current_user)):
    return {"msg": f"Hello User {user.username}"}
