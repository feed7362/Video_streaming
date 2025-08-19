from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent


class BaseAppSettings(BaseSettings):
    class Config:
        env_file_encoding = 'utf-8'


class DatabaseSettings(BaseAppSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_NAME: str
    POSTGRES_USER: str
    POSTGRES_PASS: str

    class Config:
        env_file = str(BASE_DIR / "database.env")


class S3Settings(BaseAppSettings):
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_ENDPOINT_URL: str
    MINIO_BUCKET_NAME: str
    MINIO_REGION_NAME: str

    class Config:
        env_file = str(BASE_DIR / "s3.env")


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache()
def get_s3_settings() -> S3Settings:
    return S3Settings()
