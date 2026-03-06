from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileMeta(BaseModel):
    file_id: UUID
    filename: str
    size: float


class FileResponse(BaseModel):
    status: Literal["accepted", "duplicate", "deleted"]
    files: List[FileMeta]


class FileStreamResponse(BaseModel):
    filename: str
    media_type: str

    model_config = {
        "json_schema_extra": {
            "example": {
                "filename": "video_720p.mp4",
                "media_type": "application/vnd.apple.mpegurl",
            }
        }
    }


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    code: str
    message: str


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


class PaginationQuery(BaseModel):
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Page size")
