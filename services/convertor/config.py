from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class BaseAppSettings(BaseSettings):
    class Config:
        model_config = SettingsConfigDict(env_file_encoding="utf-8")


class S3Settings(BaseAppSettings):
    MINIO_ROOT_USER: Optional[str] = Field(default=None)
    MINIO_ROOT_PASSWORD: Optional[str] = Field(default=None)
    MINIO_ENDPOINT_URL: Optional[str] = Field(default=None)
    MINIO_BUCKET_NAME: Optional[str] = Field(default=None)
    MINIO_REGION_NAME: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / "s3.env"))


@lru_cache()
def get_s3_settings() -> S3Settings:
    return S3Settings()
