from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from src.schemas.video import ResolutionMeta


class StatusMessage(BaseModel):
    video_id: UUID
    status: str
    resolutions: Optional[List[ResolutionMeta]] = None
    video_path: Optional[str] = None
