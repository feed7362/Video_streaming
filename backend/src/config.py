from functools import lru_cache
from pydantic_settings import BaseSettings


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
        env_file = './database.env'
        env_prefix = 'POSTGRES_'

class S3Settings(BaseAppSettings):
    ACCESS_KEY: str
    SECRET_KEY: str
    ENDPOINT_URL: str
    BUCKET_NAME: str

    class Config:
        env_file = './s3.env'


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings()


@lru_cache()
def get_s3_settings() -> S3Settings:
    return S3Settings()