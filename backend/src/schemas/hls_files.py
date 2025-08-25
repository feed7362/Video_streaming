from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class HLSFileBase(BaseModel):
    resolution: str
    url: str


class HLSFileCreate(HLSFileBase):
    pass


class HLSFileRead(HLSFileBase):
    id: UUID
    video_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
