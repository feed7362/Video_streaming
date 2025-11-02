from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class PrivacyLevel(str, Enum):
    public = "public"
    private = "private"


class PrivacyResponse(BaseModel):
    video_id: UUID
    old_privacy: str
    updated_privacy: str
