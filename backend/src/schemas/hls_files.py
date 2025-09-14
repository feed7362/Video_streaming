from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HLSFileBase(BaseModel):
    resolution: str
    url: str


class HLSFileCreate(HLSFileBase):
    pass


class HLSFileRead(BaseModel):
    id: UUID
    video_id: UUID
    resolution: str
    url: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
