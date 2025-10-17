from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel


class Comment(BaseModel):
    id: UUID
    video_id: UUID
    created_at: datetime
    author: str
    text: str

    class Config:
        orm_mode = True


class CommentPage(BaseModel):
    items: List[Comment]
    page: int
    size: int
    total: int
