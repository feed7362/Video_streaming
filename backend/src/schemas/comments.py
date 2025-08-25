from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    video_id: UUID


class CommentRead(CommentBase):
    id: UUID
    video_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
