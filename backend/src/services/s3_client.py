from contextlib import asynccontextmanager
from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from ..config import get_s3_settings

settings = get_s3_settings()


class S3Client:
    def __init__(
            self,
            access_key: str,
            secret_key: str,
            endpoint_url: str,
            bucket_name: str,
    ):
        self.config = {
            "access_key_id": access_key,
            "secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self):
        """
        Async context manager to create and yield an S3 client.

        This method initializes an S3 client using the session and configuration
        provided in the class instance and ensures proper cleanup after usage.

        Yields:
            aiobotocore.client.AioBaseClient: An asynchronous S3 client instance.
        """
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def upload_file(self, filename: str, file_obj):
        try:
            async with self._get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=filename,
                    Body=file_obj,
                )
                print(f"File {filename} uploaded to {self.bucket_name}")
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
                print(f"File {object_name} deleted from {self.bucket_name}")
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def download_file(self, object_name: str, chunk_size: int):
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=self.bucket_name, Key=object_name)
                async for chunk in response['Body'].iter_chunks(chunk_size):
                    yield chunk
                print(f"File {object_name} downloaded with chunk size {chunk_size}")
        except ClientError as e:
            print(f"Error downloading file: {e}")


s3_client = S3Client(
    settings.MINIO_ACCESS_KEY,
    settings.MINIO_SECRET_KEY,
    settings.MINIO_ENDPOINT_URL,
    settings.MINIO_BUCKET_NAME,
)
