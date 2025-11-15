from datetime import datetime
from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.models import User


class UserRead(BaseModel):
    id: UUID
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentUser(BaseModel):
    user_id: UUID
    username: str
    email: str
    roles: List[str]
    token: Dict

    model_config = ConfigDict(from_attributes=True)


def to_current_user(user: User, roles: list[str], token: dict) -> CurrentUser:
    return CurrentUser(
        user_id=user.id,
        username=user.username,
        email=user.email,
        roles=roles,
        token=token,
    )
