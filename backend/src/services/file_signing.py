import re

from src.errors.files import (
    FileNotFoundS3Error,
    InvalidFilePathError,
    SignedUrlGenerationError,
)


def parse_minio_path(file_path: str):
    match = re.match(r"^/minio/([^/]+)/(.*)$", file_path)
    if not match:
        raise InvalidFilePathError()
    return match.groups()


class FileSigningService:
    def __init__(self, s3_client, expires_in=3600):
        self.s3_client = s3_client
        self.expires_in = expires_in

    async def create_signed_url(self, file_path: str):
        bucket, key = parse_minio_path(file_path)

        try:
            signed_url = await self.s3_client.generate_presigned_url(
                object_key=key,
                client_method="get_object",
                expires_in=self.expires_in,
                bucket_name=bucket,
            )
        except Exception as e:
            raise SignedUrlGenerationError(str(e))

        if not signed_url:
            raise FileNotFoundS3Error(f"{key} not found in {bucket}")

        return {
            "path": key,
            "signed_url": signed_url,
            "expires_in": 3600,
        }
