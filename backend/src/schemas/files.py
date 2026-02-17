from pydantic import BaseModel


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
