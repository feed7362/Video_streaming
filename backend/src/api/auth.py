import secrets

import bcrypt
import httpx
import jwt as pyjwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import get_github_oauth_settings, get_jwt_settings
from src.infrastructure.auth import (
    current_active_user,
    current_superuser,
    fastapi_users,
    get_jwt_strategy,
    get_user_manager,
    github_oauth_client,
)
from src.infrastructure.database import get_async_session
from src.models import OAuthAccount, User
from src.schemas.user import (
    CheckUserRequest,
    CheckUserResponse,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserPublic,
    UserRead,
)

_github_settings = get_github_oauth_settings()
_jwt_settings = get_jwt_settings()

router_auth = APIRouter(
    prefix="/api/auth",
    tags=["auth"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)

# Include fastapi-users register router
router_auth.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
)

# Include fastapi-users reset password router
router_auth.include_router(
    fastapi_users.get_reset_password_router(),
)

# Include fastapi-users verify router
router_auth.include_router(
    fastapi_users.get_verify_router(UserRead),
)


@router_auth.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    user_manager=Depends(get_user_manager),
) -> LoginResponse:
    user = await user_manager.authenticate(
        credentials=type(
            "Credentials", (), {"username": data.email, "password": data.password}
        )()
    )
    if user is None or not user.is_active:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    strategy = get_jwt_strategy()
    token = await strategy.write_token(user)
    return LoginResponse(token=token)


@router_auth.post("/logout")
async def logout() -> dict:
    return {"detail": "Logged out"}


@router_auth.get("/me", response_model=UserPublic)
async def get_me(user: User = Depends(current_active_user)) -> UserPublic:
    return UserPublic.model_validate(user)


@router_auth.get("/admin")
async def admin_panel(user: User = Depends(current_superuser)) -> dict:
    return {"msg": f"Hello Admin {user.username}"}


@router_auth.post("/check-user", response_model=CheckUserResponse)
async def check_user(
    data: CheckUserRequest,
    session: AsyncSession = Depends(get_async_session),
) -> CheckUserResponse:
    username_result = await session.execute(
        select(User).where(User.username == data.username)
    )
    email_result = await session.execute(select(User).where(User.email == data.email))
    return CheckUserResponse(
        usernameExists=username_result.scalar_one_or_none() is not None,
        emailExists=email_result.scalar_one_or_none() is not None,
    )


@router_auth.get("/users/{username}", response_model=UserPublic)
async def get_user_by_username(
    username: str,
    session: AsyncSession = Depends(get_async_session),
) -> UserPublic:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user)


# ── GitHub OAuth ──────────────────────────────────────────────────────────────


@router_auth.get("/github/authorize")
async def github_authorize() -> dict:
    """Return the GitHub authorization URL for the frontend to redirect to."""
    state = pyjwt.encode(
        {"csrf": secrets.token_urlsafe(16)},
        _jwt_settings.JWT_SECRET,
        algorithm="HS256",
    )
    authorization_url = await github_oauth_client.get_authorization_url(
        redirect_uri=_github_settings.GITHUB_CALLBACK_URL,
        state=state,
        scope=["user:email"],
    )
    return {"authorization_url": authorization_url}


@router_auth.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    session: AsyncSession = Depends(get_async_session),
) -> RedirectResponse:
    """Exchange GitHub OAuth code for a JWT and redirect to the frontend."""
    # Validate state (CSRF protection)
    try:
        pyjwt.decode(state, _jwt_settings.JWT_SECRET, algorithms=["HS256"])
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    # Exchange code for GitHub access token
    try:
        token_data = await github_oauth_client.get_access_token(
            code=code,
            redirect_uri=_github_settings.GITHUB_CALLBACK_URL,
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to exchange GitHub code")

    access_token = token_data["access_token"]

    # Fetch GitHub user info
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json",
            },
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to fetch GitHub user info"
            )
        github_data = resp.json()

        # GitHub may not expose email on /user — fetch from /user/emails
        email = github_data.get("email")
        if not email:
            emails_resp = await client.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/json",
                },
            )
            if emails_resp.status_code == 200:
                for entry in emails_resp.json():
                    if entry.get("primary") and entry.get("verified"):
                        email = entry["email"]
                        break

    if not email:
        raise HTTPException(
            status_code=400, detail="GitHub account has no accessible email"
        )

    github_id = str(github_data["id"])
    github_login = github_data.get("login", f"user_{github_id}")

    # Find existing OAuth account link
    oauth_result = await session.execute(
        select(OAuthAccount).where(
            OAuthAccount.oauth_name == "github",
            OAuthAccount.account_id == github_id,
        )
    )
    oauth_account = oauth_result.scalar_one_or_none()

    if oauth_account:
        user = await session.get(User, oauth_account.user_id)
    else:
        # Find user by email
        user_result = await session.execute(select(User).where(User.email == email))
        user = user_result.scalar_one_or_none()

        if not user:
            # Generate unique username
            username = github_login
            taken = await session.execute(select(User).where(User.username == username))
            if taken.scalar_one_or_none():
                username = f"{github_login}_{github_id[:6]}"

            user = User(
                email=email,
                username=username,
                hashed_password=bcrypt.hashpw(
                    secrets.token_bytes(32), bcrypt.gensalt()
                ).decode(),
                is_active=True,
                is_superuser=False,
                is_verified=True,
            )
            session.add(user)
            await session.flush()

        # Link GitHub account
        new_oauth = OAuthAccount(
            oauth_name="github",
            access_token=access_token,
            account_id=github_id,
            account_email=email,
            user_id=user.id,
        )
        session.add(new_oauth)
        await session.commit()

    # Issue JWT
    strategy = get_jwt_strategy()
    jwt_token = await strategy.write_token(user)

    # Redirect to frontend callback page with token
    frontend_url = _github_settings.FRONTEND_URL
    return RedirectResponse(url=f"{frontend_url}/auth/callback?token={jwt_token}")
