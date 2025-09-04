import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, BinaryIO, Dict, Optional

from aiobotocore.session import AioBaseClient, get_session
from botocore.exceptions import ClientError

from ..config import get_s3_settings

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

    async def check_bucket_exists(self) -> None:
        async with self._get_client() as client:
            try:
                await client.head_bucket(Bucket=self.bucket_name)
                logging.info(f"Bucket '{self.bucket_name}' already exists")
            except ClientError:
                await client.create_bucket(Bucket=self.bucket_name)
                await client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={"Status": "Enabled"},
                )
                await client.put_bucket_cors(
                    Bucket=self.bucket_name,
                    CORSConfiguration={
                        "CORSRules": [
                            {
                                "AllowedHeaders": ["Authorization"],
                                "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                                "AllowedOrigins": ["*"],
                                "ExposeHeaders": ["ETag", "x-amz-request-id"],
                                "MaxAgeSeconds": 3000,
                            }
                        ]
                    },
                )
                logging.info(
                    f"Bucket '{self.bucket_name}' with versioning and cors created"
                )

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
                    Bucket=self.bucket_name, Key=filename, ServerSideEncryption="AES256"
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

    async def delete_file(self, object_name: str) -> None:
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                logging.info(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            logging.error(f"Error deleting file: {e}")

    async def list_objects(self, bucket: str) -> list[str]:
        """
        Lists objects in a bucket.
        :param bucket: The name of the bucket.
        :return: The list of objects in the bucket.
        """
        try:
            async with self._get_client() as client:
                response = await client.list_objects_v2(Bucket=bucket)
                return response.get("Contents", [])
        except ClientError as client_error:
            logging.error(
                "Couldn't list objects in bucket %s. Here's why: %s",
                bucket,
                client_error.response["Error"]["Message"],
            )
            raise

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
                    async with resp["Body"] as stream:
                        while True:
                            chunk = await stream.read(chunk_size)
                            if not chunk:
                                break
                            yield chunk
                logging.info(
                    f"File {object_name} downloaded with chunk size {chunk_size}"
                )
        except ClientError as e:
            logging.error(f"Error downloading file: {e}")

    async def generate_presigned_url(
        self, object_name: str, client_method: str, expires_in: int = 100
    ) -> str | None:
        try:
            async with self._get_client() as client:
                url = await client.generate_presigned_url(
                    ClientMethod=client_method,
                    Params={"Bucket": self.bucket_name, "Key": object_name},
                    ExpiresIn=expires_in,
                )
                logging.info(f"Presigned URL generated for file '{object_name}'.")
                return url
        except ClientError:
            logging.error(
                f"Couldn't get a presigned URL for client method '{client_method}'."
            )
            return None


_s3_client_instance: Optional[S3Client] = None


def get_s3_client() -> S3Client:
    """
    Lazy initialization of the S3 client.
    The client will only be created on the first call to this function.
    """
    settings = get_s3_settings()
    global _s3_client_instance
    if _s3_client_instance is None:
        _s3_client_instance = S3Client(
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            endpoint_url=settings.MINIO_ENDPOINT_URL,
            bucket_name=settings.MINIO_BUCKET_NAME,
            region_name=settings.MINIO_REGION_NAME,
        )
    return _s3_client_instance
