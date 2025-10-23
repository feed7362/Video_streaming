from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from .enum import Privacy, VideoStatus

# Generic type for reusable pagination
T = TypeVar("T")


# ------------------------------
# Video Processing / Pipeline
# ------------------------------
class VideoProcessingJob(BaseModel):
    video_id: UUID
    size: float
    status: VideoStatus  # e.g., "queued", "processing", "done", "failed"
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None


class VideoProcessingResult(BaseModel):
    video_id: UUID
    resolutions: List[str]  # ["360p", "720p", "1080p"]
    duration: float  # seconds
    thumbnail_url: Optional[str] = None


# ------------------------------
# Video Playback / Listing
# ------------------------------
class VideoPlayback(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    privacy: Privacy
    created_at: datetime

    # Available resolution variants
    resolutions: List[str] = Field(default_factory=list)

    # UI / metadata
    thumbnail_url: Optional[str] = None
    avatar_url: Optional[str] = None
    channel_name: str
    likes_count: int
    dislikes_count: int
    views_count: int

    # Playback source
    master_hls_url: Optional[str] = None

    class Config:
        orm_mode = True


class VideoRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ------------------------------
# Generic Pagination Schema
# ------------------------------
class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


# ------------------------------
# Video Pagination Schema
# ------------------------------
class VideoPage(Page[VideoPlayback]):
    """Paginated list of videos."""

    pass
