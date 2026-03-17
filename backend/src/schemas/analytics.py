from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class DailyMetric(BaseModel):
    date: str  # "YYYY-MM-DD"
    count: int


class TopVideo(BaseModel):
    id: UUID
    title: str
    thumbnail: str
    views_count: int
    likes_count: int
    comments_count: int


class VideoStat(BaseModel):
    id: UUID
    title: str
    thumbnail: str
    privacy: str
    views_count: int
    likes_count: int
    dislikes_count: int
    comments_count: int
    created_at: datetime


class OverviewResponse(BaseModel):
    total_views: int
    total_subscribers: int
    total_likes: int
    total_comments: int
    views_per_day: List[DailyMetric]
    top_videos: List[TopVideo]


class ContentResponse(BaseModel):
    videos: List[VideoStat]


class AudienceResponse(BaseModel):
    subscribers_per_day: List[DailyMetric]
    unique_viewers: int
    returning_viewers: int
    comments_per_day: List[DailyMetric]
