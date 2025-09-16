from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from .enum import Privacy, VideoStatus


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


class VideoPlayback(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    privacy: Privacy
    created_at: datetime
    resolutions: List[str] = []  # available variants

    # UI/UX
    thumbnail_url: Optional[str] = None
    avatar_url: Optional[str] = None
    channel_name: str
    likes_count: int
    dislikes_count: int
    views_count: int

    master_hls_url: Optional[str] = None
