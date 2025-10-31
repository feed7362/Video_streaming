from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel

from ..schemas.video import ResolutionMeta


class FileMeta(BaseModel):
    file_id: UUID
    filename: str
    size: float


class FileResponse(BaseModel):
    status: Literal["accepted", "duplicate", "deleted"]
    files: List[FileMeta]


class FileStreamResponse(BaseModel):
    filename: str
    media_type: str = "application/octet-stream"


class ErrorResponse(BaseModel):
    status: str = "error"
    message: str


class StatusMessage(BaseModel):
    video_id: UUID
    status: str
    resolutions: Optional[List[ResolutionMeta]] = None
    video_path: Optional[str] = None


class HealthStatus(BaseModel):
    status: str
    details: Optional[Dict[str, str]] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "ok"},
                {
                    "status": "ready",
                    "details": {
                        "database": "ok",
                        "object_storage": "ok",
                    },
                },
                {
                    "status": "not ready",
                    "details": {
                        "database": "error: OperationalError",
                        "object_storage": "ok",
                    },
                },
            ]
        }
    }


class SignedUrlResponse(BaseModel):
    path: str
    signed_url: str
    expires_in: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "path": "123e4567-e89b-12d3-a456-426614174000/master.m3u8",
                    "signed_url": "https://example.com/presigned-url",
                    "expires_in": 3600,
                }
            ]
        }
    }


class APIError(BaseModel):
    detail: str
    status_code: int
    type: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Invalid request parameters",
                    "status_code": 400,
                    "type": "BadRequest",
                },
                {"detail": "Unauthorized", "status_code": 401, "type": "Unauthorized"},
                {
                    "detail": "Internal server error",
                    "status_code": 500,
                    "type": "ServerError",
                },
            ]
        }
    }
