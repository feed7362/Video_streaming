import os
from functools import lru_cache
from typing import List, Optional

import hvac
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv("VAULT_ADDR"),
            token=os.getenv("VAULT_TOKEN"),
        )
        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed")

    def read_secret(self, path: str, mount_point: str) -> dict:
        secret = self.client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=mount_point
        )
        return secret["data"]["data"]


vault = VaultClient()


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8")


class DatabaseSettings(BaseAppSettings):
    POSTGRES_HOST: Optional[str] = Field(default=None)
    POSTGRES_PORT: Optional[str] = Field(default=None)
    POSTGRES_DB: Optional[str] = Field(default=None)
    POSTGRES_USER: Optional[str] = Field(default=None)
    POSTGRES_PASSWORD: Optional[str] = Field(default=None)


class S3Settings(BaseAppSettings):
    MINIO_ROOT_USER: Optional[str] = Field(default=None)
    MINIO_ROOT_PASSWORD: Optional[str] = Field(default=None)
    MINIO_ENDPOINT_URL: Optional[str] = Field(default=None)
    MINIO_REGION_NAME: Optional[str] = Field(default=None)
    BUCKET_NAMES: Optional[List[str]] = Field(default=None)


@lru_cache()
def get_database_settings() -> DatabaseSettings:
    return DatabaseSettings(**vault.read_secret("database", mount_point="secret"))


@lru_cache()
def get_s3_settings() -> S3Settings:
    data = vault.read_secret("s3", mount_point="secret")
    data["BUCKET_NAMES"] = [b.strip() for b in data["BUCKET_NAMES"].split(",")]
    return S3Settings(**data)
