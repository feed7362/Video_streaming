from uuid import UUID

from fastapi import Depends

from src.infrastructure.auth import current_active_user, current_optional_user
from src.models import User


async def get_current_user_id(
    user: User = Depends(current_active_user),
) -> UUID:
    return user.id


async def get_optional_user_id(
    user: User | None = Depends(current_optional_user),
) -> UUID | None:
    return user.id if user else None
