import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator, BinaryIO, Dict

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
        bucket_name: str,
        region_name: str,
    ):
        self.config: Dict[str, str] = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
            "region_name": region_name,
        }
        self.bucket_name = bucket_name
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

    async def upload_file(self, filename: str, file_obj: BinaryIO) -> None:
        try:
            async with self._get_client() as client:
                resp = await client.create_multipart_upload(
                    Bucket=self.bucket_name, Key=filename
                )
                upload_id = resp["UploadId"]
                parts = []
                part_number = 1

                while True:
                    chunk = file_obj.read(PART_SIZE)
                    if not chunk:
                        break
                    part_resp = await client.upload_part(
                        Bucket=self.bucket_name,
                        Key=filename,
                        PartNumber=part_number,
                        UploadId=upload_id,
                        Body=chunk,
                    )
                    parts.append({"ETag": part_resp["ETag"], "PartNumber": part_number})
                    part_number += 1

                await client.complete_multipart_upload(
                    Bucket=self.bucket_name,
                    Key=filename,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
                logging.info(f"File {filename} uploaded to {self.bucket_name}")
        except ClientError as e:
            await client.abort_multipart_upload(
                Bucket=self.bucket_name, Key=filename, UploadId=upload_id
            )
            logging.error(f"Error uploading file: {e}")

    async def upload_dir(self, dirname: str, directory: Path) -> None:
        try:
            for p in Path(directory).rglob("*"):
                if p.is_file():
                    await self.upload_file(
                        str(dirname / p.relative_to(directory)), p.open("rb")
                    )
        except ClientError as e:
            logging.error(f"Error uploading dir: {e}")

    async def delete_file(self, object_name: str) -> None:
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                logging.info(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            logging.error(f"Error deleting file: {e}")

    async def download_file(
        self, object_name: str, chunk_size: int
    ) -> AsyncGenerator[bytes, None]:
        try:
            async with self._get_client() as client:
                head = await client.head_object(
                    Bucket=self.bucket_name, Key=object_name
                )
                size = head["ContentLength"]

                for start in range(0, size, chunk_size):
                    end = min(start + chunk_size - 1, size - 1)
                    resp = await client.get_object(
                        Bucket=self.bucket_name,
                        Key=object_name,
                        Range=f"bytes={start}-{end}",
                    )
                    yield await resp["Body"].read()
                logging.info(
                    f"File {object_name} downloaded with chunk size {chunk_size}"
                )
        except ClientError as e:
            logging.error(f"Error downloading file: {e}")


s3_client = S3Client(
    settings.MINIO_ROOT_USER,
    settings.MINIO_ROOT_PASSWORD,
    settings.MINIO_ENDPOINT_URL,
    settings.MINIO_BUCKET_NAME,
    settings.MINIO_REGION_NAME,
)
