from datetime import datetime
from typing import Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models import Video

# Generic type for reusable pagination
T = TypeVar("T")


class ResolutionMeta(BaseModel):
    height: int
    width: int
    bitrate: int
    playlist_path: str


# ------------------------------
# Video Processing / Pipeline
# ------------------------------
class VideoProcessingJob(BaseModel):
    video_id: UUID
    size: float
    status: str
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
    privacy: str
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

    model_config = ConfigDict(from_attributes=True)


class VideoRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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
class VideoPreview(BaseModel):
    """Lightweight preview used for video listings or home page."""

    id: UUID
    title: str
    thumbnail: str
    channel_avatar: str
    channel_name: str
    views_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


def to_video_preview(video: Video) -> VideoPreview:
    return VideoPreview(
        id=video.id,
        title=video.name,
        thumbnail=video.thumbnail_path or "",
        channel_avatar=getattr(video.channel, "avatar_url", ""),
        channel_name=getattr(video.channel, "name", "Unknown Channel"),
        views_count=video.views_count,
        created_at=video.created_at,
    )


def map_video_to_playback(video: Video, resolutions: list[str]) -> VideoPlayback:
    return VideoPlayback(
        id=video.id,
        name=video.name,
        description=video.description,
        created_at=video.created_at,
        master_hls_url=video.video_path,
        privacy=video.privacy.name,
        resolutions=resolutions,
        channel_name=video.channel.name,
        likes_count=video.likes_count,
        dislikes_count=video.dislikes_count,
        views_count=video.views_count + 1,
        thumbnail_url=video.thumbnail_path,
        avatar_url=video.channel.avatar_path,
    )


class VideoPreviewPage(Page[VideoPreview]):
    """Paginated list of lightweight video previews."""

    pass


class VideoPage(BaseModel):
    """Paginated list of videos."""

    pass
