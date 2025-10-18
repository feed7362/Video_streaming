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
