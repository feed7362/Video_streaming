from typing import List

from pydantic import BaseModel


class FileMeta(BaseModel):
    filename: str
    size: int


class UploadResponse(BaseModel):
    status: str
    files_count: int
    files: List[FileMeta]


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


class StatusMessage(BaseModel):
    video_id: str
    status: str
