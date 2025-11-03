import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, BinaryIO, Dict, List, Optional

from aiobotocore.session import AioBaseClient, get_session
from botocore.exceptions import ClientError

from config import get_s3_settings

settings = get_s3_settings()
PART_SIZE = 1024 * 1024 * 10


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        region_name: str,
        bucket_names: List[str],
    ):
        self.bucket_names = bucket_names
        self.config: Dict[str, str] = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AioBaseClient, None]:
        """
        Async context manager to create and yield an S3 client.

        This method initializes an S3 client using the session and configuration
        provided in the class instance and ensures proper cleanup after usage.

        Yields:
            aiobotocore.client.AioBaseClient: An asynchronous S3 client instance.
        """
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(
        self, filename: str, file_obj: BinaryIO, bucket_name: Optional[str] = None
    ) -> None:
        upload_id = None
        if not bucket_name:
            raise ValueError("bucket_name must be provided")
        elif bucket_name not in self.bucket_names:
            raise ValueError("bucket_name is not in bucket_names")
        try:
            async with self._get_client() as client:
                resp = await client.create_multipart_upload(
                    Bucket=bucket_name, Key=filename
                )
                upload_id = resp["UploadId"]
                parts = []
                part_number = 1

                while True:
                    chunk = file_obj.read(PART_SIZE)
                    if not chunk:
                        break
                    part_resp = await client.upload_part(
                        Bucket=bucket_name,
                        Key=filename,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=chunk,
                    )
                    parts.append({"ETag": part_resp["ETag"], "PartNumber": part_number})
                    part_number += 1

                await client.complete_multipart_upload(
                    Bucket=bucket_name,
                    Key=filename,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
                logging.info(f"File {filename} uploaded to {bucket_name}")
        except ClientError as e:
            if upload_id is not None:
                await client.abort_multipart_upload(
                    Bucket=bucket_name, Key=filename, UploadId=upload_id
                )
            logging.error(f"Error uploading file: {e}")

    async def upload_dir(
        self, dirname: str, directory: Path, bucket_name: Optional[str] = None
    ) -> None:
        try:
            for p in Path(directory).rglob("*"):
                if p.is_file():
                    await self.upload_file(
                        str(dirname / p.relative_to(directory)),
                        p.open("rb"),
                        bucket_name,
                    )
        except ClientError as e:
            logging.error(f"Error uploading dir: {e}")

    async def delete_file(
        self, object_name: str, bucket_name: Optional[str] = None
    ) -> None:
        if not bucket_name:
            raise ValueError("bucket_name must be provided")
        elif bucket_name not in self.bucket_names:
            raise ValueError("bucket_name is not in bucket_names")
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=bucket_name, Key=object_name)
                logging.info(f"File {object_name} deleted from {bucket_name}")
        except ClientError as e:
            logging.error(f"Error deleting file: {e}")

    async def download_file(
        self, object_name: str, chunk_size: int, bucket_name: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        if not bucket_name:
            raise ValueError("bucket_name must be provided")
        elif bucket_name not in self.bucket_names:
            raise ValueError("bucket_name is not in bucket_names")
        try:
            async with self._get_client() as client:
                head = await client.head_object(Bucket=bucket_name, Key=object_name)
                size = head["ContentLength"]
                chunk_size = max(min(chunk_size, size), 1 * 1024 * 1024)

                for start in range(0, size, chunk_size):
                    end = min(start + chunk_size - 1, size - 1)
                    resp = await client.get_object(
                        Bucket=bucket_name,
                        Key=object_name,
                        Range=f"bytes={start}-{end}",
                    )
                    yield await resp["Body"].read()
                logging.info(
                    f"File {object_name} downloaded with chunk size {chunk_size}"
                )
        except ClientError as e:
            logging.error(f"Error downloading file: {e}")

    async def download_file_by_range(
        self,
        object_name: str,
        range_start: int = 0,
        range_end: int = 1024,
        bucket_name: Optional[str] = None,
    ) -> AsyncGenerator[bytes, None]:
        if not bucket_name:
            raise ValueError("bucket_name must be provided")
        elif bucket_name not in self.bucket_names:
            raise ValueError("bucket_name is not in bucket_names")
        try:
            async with self._get_client() as client:
                resp = await client.get_object(
                    Bucket=bucket_name,
                    Key=object_name,
                    Range=f"bytes={range_start}-{range_end}",
                )
                logging.info(
                    f"File {object_name} downloaded with chunk range "
                    f"{range_start} - {range_end} Bytes"
                )
                yield await resp["Body"].read()
        except ClientError as e:
            logging.error(f"Error downloading file: {e}")


_s3_client_instance: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """
    Lazy initialization of the S3 client.
    The client will only be created on the first call to this function.
    """
    settings = get_s3_settings()
    assert settings.MINIO_ROOT_USER is not None, "MINIO_ROOT_USER is not set"
    assert settings.MINIO_ROOT_PASSWORD is not None, "MINIO_ROOT_PASSWORD is not set"
    assert settings.MINIO_ENDPOINT_URL is not None, "MINIO_ENDPOINT_URL is not set"
    assert settings.MINIO_REGION_NAME is not None, "MINIO_REGION_NAME is not set"
    assert settings.BUCKET_NAMES is not None, "BUCKET_NAMES is not set"

    global _s3_client_instance
    if _s3_client_instance is None:
        _s3_client_instance = S3Client(
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            endpoint_url=settings.MINIO_ENDPOINT_URL,
            region_name=settings.MINIO_REGION_NAME,
            bucket_names=settings.BUCKET_NAMES,
        )
    return _s3_client_instance
