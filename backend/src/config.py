from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8")


class DatabaseSettings(BaseAppSettings):
    POSTGRES_HOST: Optional[str] = Field(default=None)
    POSTGRES_PORT: Optional[str] = Field(default=None)
    POSTGRES_DB: Optional[str] = Field(default=None)
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / "database.env"))


class S3Settings(BaseAppSettings):
    MINIO_ROOT_USER: Optional[str] = Field(default=None)
    MINIO_ROOT_PASSWORD: Optional[str] = Field(default=None)
    MINIO_ENDPOINT_URL: Optional[str] = Field(default=None)
    MINIO_REGION_NAME: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / "s3.env"))


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache()
def get_s3_settings() -> S3Settings:
    return S3Settings()
