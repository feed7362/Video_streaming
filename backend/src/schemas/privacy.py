from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class PrivacyLevel(str, Enum):
    public = "public"
    private = "private"


class PrivacyResponse(BaseModel):
    video_id: UUID
    old_privacy: str
    updated_privacy: str


class PrivacyUpdateRequest(BaseModel):
    updated_privacy: str = Field(
        default="public",
        description="Privacy setting: `public` or `private`",
        examples=["public", "private"],
    )

    @field_validator("updated_privacy")
    @classmethod
    def must_be_public_or_private(cls, v: str) -> str:
        if v not in {"public", "private"}:
            raise ValueError("updated_privacy must be either 'public' or 'private'")
        return v
