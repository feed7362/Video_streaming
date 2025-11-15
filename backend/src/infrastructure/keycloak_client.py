from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from keycloak import KeycloakOpenID
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_keycloak_settings
from ..models import User
from ..schemas.user import CurrentUser, to_current_user
from .database import get_async_session

bearer = HTTPBearer()
setting = get_keycloak_settings()

# --------------------------
# Init Keycloak OpenID client
# --------------------------
keycloak_openid = KeycloakOpenID(
    server_url=setting.SERVER_URL,
    client_id=setting.CLIENT_ID,
    realm_name=setting.REALM_NAME,
    client_secret_key=setting.CLIENT_SECRET_KEY,
)


# JWKS for JWT validation
async def get_certs():
    return await keycloak_openid.a_certs()


async def get_well_known():
    return await keycloak_openid.a_well_known()


# ---------------------------------------------------------
# TOKEN MANAGEMENT
# ---------------------------------------------------------
async def refresh_tokens(refresh_token: str) -> dict:
    return await keycloak_openid.a_refresh_token(refresh_token)


async def verify_access_token(token: str) -> dict:
    try:
        jwks = await get_certs()
        return await keycloak_openid.a_decode_token(
            token, key=jwks, validate=True, options={"verify_aud": False}  # JWKS (dict)
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------------------------------------------------
# ROLE MANAGEMENT
# ---------------------------------------------------------
async def extract_roles(decoded: dict) -> list[str]:
    return decoded.get("realm_access", {}).get("roles", [])


# ---------------------------------------------------------
# DB INTEGRATION
# ---------------------------------------------------------
async def get_user(decoded: dict, session: AsyncSession) -> User | None:
    user_id = decoded["sub"]
    user = await session.get(User, user_id)

    return user


async def create_user(decoded: dict, session: AsyncSession) -> User:
    user_id = decoded["sub"]
    user = await session.get(User, user_id)

    if not user:
        user = User(
            id=user_id,
            username=decoded.get("preferred_username"),
            email=decoded.get("email"),
        )
        session.add(user)
        await session.commit()

    return user


# ---------------------------------------------------------
# AUTH DEPENDENCY (used in routes)
# ---------------------------------------------------------
async def get_current_user(
    credentials=Depends(bearer),
    session: AsyncSession = Depends(get_async_session),
) -> CurrentUser:

    token = credentials.credentials
    decoded = await verify_access_token(token)
    roles = await extract_roles(decoded)

    user = await get_user(decoded, session)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return to_current_user(user=user, roles=roles, token=decoded)


# ---------------------------------------------------------
# OPTIONAL HELPERS
# ---------------------------------------------------------
def get_userinfo(token: str) -> dict:
    return keycloak_openid.userinfo(token)


def logout(refresh_token: str) -> bytes:
    return keycloak_openid.logout(refresh_token)


def require_role(role: str):
    def dependency(user=Depends(get_current_user)):
        roles = user._token["roles"]
        if role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions: requires role '{role}'",
            )
        return user

    return dependency
