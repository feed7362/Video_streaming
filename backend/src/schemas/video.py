from datetime import datetime
from typing import Annotated, Generic, List, Literal, Optional, TypeVar
from uuid import UUID

from fastapi import File, Form, UploadFile
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.models import Video

T = TypeVar("T")

VideoCategory = Literal[
    "education",
    "entertainment",
    "music",
    "gaming",
    "technology",
    "science",
    "movies",
    "sports",
    "news",
    "travel",
    "lifestyle",
    "fashion",
    "health & fitness",
    "food & cooking",
    "comedy",
    "documentary",
    "art & design",
    "business & finance",
    "animals & nature",
    "automotive",
    "history",
    "podcasts",
    "shorts",
]


class ResolutionMeta(BaseModel):
    height: int
    width: int
    bitrate: int
    playlist_path: str


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


class VideoPlayback(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    privacy: str
    created_at: datetime
    resolutions: List[str] = Field(default_factory=list)
    thumbnail_url: Optional[str] = None
    avatar_url: Optional[str] = None
    channel_name: str
    likes_count: int
    dislikes_count: int
    views_count: int
    master_hls_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VideoRead(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: List[T]
    page: int
    size: int
    total: int


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


class VideoUploadParams(BaseModel):
    # FastAPI + Pydantic v2 quirk: `field = Form(...)` as a *default* makes FastAPI
    # treat the field as a query parameter when the model is injected via Depends().
    # The reliable pattern is `Annotated[T, Form(...)]` per field.
    video: Annotated[UploadFile, File(description="A video file to upload")]
    thumbnail: Annotated[
        Optional[UploadFile], File(description="Preview image for the video")
    ] = None
    name: Annotated[str, Form(description="Name of the uploaded files.")]
    description: Annotated[
        str, Form(description="Optional description of the uploaded files.")
    ] = ""
    category: Annotated[
        VideoCategory, Form(description="Category of the uploaded files.")
    ]
    privacy: Annotated[
        Literal["public", "private"],
        Form(description="Privacy level: `public` or `private`"),
    ] = "public"

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("description")
    @classmethod
    def description_strip(cls, v: str) -> str:
        return (v or "").strip()


class VideoDownloadQuery(BaseModel):
    resolution: Optional[str] = Field(
        default=None,
        description="Specific resolution to download (e.g., '360p', '720p', '1080p'). "
        "If omitted, original file is returned.",
    )
