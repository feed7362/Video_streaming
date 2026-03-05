from functools import lru_cache
from typing import List, Optional

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.infrastructure.vault import VaultClient

vault = VaultClient()


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8")


class DatabaseSettings(BaseAppSettings):
    POSTGRES_HOST: Optional[str] = Field(default=None)
    POSTGRES_PORT: Optional[str] = Field(default=None)
    POSTGRES_DB: Optional[str] = Field(default=None)
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)

    @computed_field
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


class S3Settings(BaseAppSettings):
    MINIO_ROOT_USER: Optional[str] = Field(default=None)
    MINIO_ROOT_PASSWORD: Optional[str] = Field(default=None)
    MINIO_ENDPOINT_URL: Optional[str] = Field(default=None)
    MINIO_REGION_NAME: Optional[str] = Field(default=None)
    BUCKET_NAMES: Optional[List[str]] = Field(default=None)


class ElasticSettings(BaseAppSettings):
    ELASTIC_HOST: Optional[str] = Field(default=None)
    ELASTIC_PASSWORD: Optional[str] = Field(default=None)


class KeycloakSettings(BaseAppSettings):
    CLIENT_ID: Optional[str] = Field(default=None)
    CLIENT_SECRET_KEY: Optional[str] = Field(default=None)
    REALM_NAME: Optional[str] = Field(default=None)
    SERVER_URL: Optional[str] = Field(default=None)


class RedisSettings(BaseAppSettings):
    REDIS_HOST: Optional[str] = Field(default=None)
    REDIS_PORT: Optional[int] = Field(default=None)


class RABBITMQSettings(BaseAppSettings):
    RABBITMQ_HOST: Optional[str] = Field(default=None)
    RABBITMQ_PORT: Optional[str] = Field(default=None)
    RABBITMQ_USER: Optional[str] = Field(default=None)
    RABBITMQ_PASSWORD: Optional[str] = Field(default=None)

    @computed_field
    def rabbitmq_url(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"
        )


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings(**vault.read_secret("database", mount_point="secret"))


@lru_cache()
def get_s3_settings() -> S3Settings:
    data = vault.read_secret("s3", mount_point="secret")
    data["BUCKET_NAMES"] = [b.strip() for b in data["BUCKET_NAMES"].split(",")]
    return S3Settings(**data)


@lru_cache()
def get_elastic_settings() -> ElasticSettings:
    return ElasticSettings(**vault.read_secret("elastic", mount_point="secret"))


@lru_cache()
def get_keycloak_settings() -> KeycloakSettings:
    return KeycloakSettings(**vault.read_secret("keycloak", mount_point="secret"))


@lru_cache()
def get_redis_settings() -> RedisSettings:
    return RedisSettings(**vault.read_secret("redis", mount_point="secret"))


@lru_cache()
def get_rabbitmq_settings() -> RABBITMQSettings:
    return RABBITMQSettings(**vault.read_secret("rabbitmq", mount_point="secret"))
