import logging
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

import xxhash
from fastapi import UploadFile
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..errors.files import (
    ChannelNotFoundError,
    DuplicateVideoError,
    InvalidThumbnailFormatError,
    InvalidVideoFormatError,
    JobPublishFailedError,
    ResolutionNotFoundError,
    S3DeletionError,
    S3DownloadError,
    VideoNotFoundError,
)
from ..models.channel import Channel
from ..models.video import Video
from ..models.video_resolutions import VideoResolution
from ..schemas.endpoint import FileMeta, FileResponse

if TYPE_CHECKING:
    from faststream.rabbit import RabbitBroker

    from ..infrastructure.s3_client import S3Client


async def _hash_and_size(uploaded_file):
    hasher = xxhash.xxh3_128()
    block_size = 1024 * 1024

    await uploaded_file.seek(0)
    size = 0

    # hash + size in one pass
    while chunk := await uploaded_file.read(block_size):
        hasher.update(chunk)
        size += len(chunk)
    await uploaded_file.seek(0)
    return hasher.hexdigest(), size


class FileService:
    def __init__(
        self,
        session: AsyncSession,
        s3_client: "S3Client",
        broker: Optional["RabbitBroker"] = None,
    ):
        self.session = session
        self.s3_client = s3_client
        self.broker = broker

    async def _get_channel_id(self, user_id: UUID) -> UUID:
        result = await self.session.execute(
            select(Channel.id).where(Channel.user_id == user_id)
        )
        channel_id = result.scalar_one_or_none()

        if not channel_id:
            raise ChannelNotFoundError()

        return channel_id

    async def _upload_thumbnail(self, video_id, thumbnail):
        thumb_suffix = Path(thumbnail.filename or "").suffix
        thumbnail_id = str(uuid4())
        thumb_name = f"{thumbnail_id}{thumb_suffix}"
        await self.s3_client.upload_file(
            thumb_name, thumbnail.file, bucket_name="video-thumbnails"
        )
        await self.session.execute(
            update(Video)
            .where(Video.id == video_id)
            .values(thumbnail_path=f"/minio/video-thumbnails/{thumb_name}")
        )
        await self.session.commit()

    async def _upload_video_file(self, video_id, video):
        video_suffix = Path(video.filename or "").suffix
        new_filename = f"{video_id}{video_suffix}"
        await self.s3_client.upload_file(new_filename, video.file, bucket_name="videos")
        return new_filename

    async def _insert_video(
        self,
        video_id,
        name,
        description,
        channel_id,
        video_size,
        video_hash,
        privacy,
        category,
    ):
        result = await self.session.execute(
            insert(Video)
            .values(
                id=video_id,
                name=name,
                description=description,
                channel_id=channel_id,
                size=video_size,
                hash=video_hash,
                video_path=None,
                thumbnail_path=None,
                privacy_id=uuid5(NAMESPACE_DNS, f"privacy_status:{privacy}"),
                category_id=uuid5(NAMESPACE_DNS, f"video_category:{category}"),
                status_id=uuid5(NAMESPACE_DNS, "video_status:queued"),
            )
            .on_conflict_do_nothing(index_elements=["hash"])
            .returning(Video.id)
        )
        inserted_id = result.scalar_one_or_none()
        await self.session.commit()
        return inserted_id

    async def upload_video(
        self,
        *,
        video: UploadFile,
        thumbnail: UploadFile | None,
        name: str,
        description: str,
        privacy: str,
        category: str,
        user_id: UUID,
    ) -> FileResponse:

        if not (video.content_type or "").startswith("video/"):
            raise InvalidVideoFormatError()

        if thumbnail and not (thumbnail.content_type or "").startswith("image/"):
            raise InvalidThumbnailFormatError()

        video_hash, video_size = await _hash_and_size(video)
        video_id = uuid.uuid4()

        channel_id = await self._get_channel_id(user_id)
        if not channel_id:
            raise ChannelNotFoundError()

        inserted = await self._insert_video(
            video_id,
            name,
            description,
            channel_id,
            video_size,
            video_hash,
            privacy,
            category,
        )

        if not inserted:
            raise DuplicateVideoError(inserted)

        if thumbnail:
            await self._upload_thumbnail(video_id, thumbnail)

        filename = await self._upload_video_file(video_id, video)

        try:
            if self.broker is None:
                raise RuntimeError("Broker is not configured")

            await self.broker.publish(
                filename,
                queue="video.encode",
                priority=10,
            )
        except Exception as e:
            logging.error(f"Upload pipeline failed for {video_id}: {e}")

            await self.session.execute(delete(Video).where(Video.id == video_id))
            await self.session.commit()
            raise JobPublishFailedError()

        return FileResponse(
            status="accepted",
            files=[
                FileMeta(
                    file_id=video_id,
                    filename=name,
                    size=video_size,
                )
            ],
        )

    async def get_video_file(
        self, video_id: UUID, user_id: UUID, resolution: Optional[str] = None
    ) -> tuple[str, str, str]:
        """Return (object_key, filename, media_type) for streaming"""
        result = await self.session.execute(
            select(Video)
            .join(Channel, Channel.id == Video.channel_id)
            .where(Video.id == video_id, Channel.user_id == user_id)
        )
        video = result.scalar_one_or_none()
        if not video:
            raise VideoNotFoundError()

        if resolution:
            target_height = int(resolution.rstrip("p"))
            res_result = await self.session.execute(
                select(VideoResolution).where(
                    (VideoResolution.video_id == video_id)
                    & (VideoResolution.height == target_height)
                )
            )
            res_obj = res_result.scalar_one_or_none()
            if not res_obj:
                raise ResolutionNotFoundError(resolution)
            object_key = res_obj.playlist_path.lstrip("/")
            filename = f"{video.name}_{res_obj.height}p.m3u8"
            media_type = "application/vnd.apple.mpegurl"
        else:
            # Default/original file
            object_key = str(video.id)
            filename = f"{video.name}.mp4"
            media_type = "video/mp4"

        return object_key, filename, media_type

    def stream_file(
        self,
        object_key: str,
        bucket_name: str = "videos",
        chunk_size: int = 1024 * 1024 * 3,
    ):
        """Returns a generator for StreamingResponse"""
        try:
            return self.s3_client.download_file(
                object_key, chunk_size, bucket_name=bucket_name
            )
        except Exception as e:
            logging.error(f"S3 streaming error for {object_key}: {e}")
            raise S3DownloadError(object_key)

    async def delete_video(self, video_id, user_id):
        # Fetch video & check ownership
        result = await self.session.execute(
            select(Video)
            .join(Channel, Channel.id == Video.channel_id)
            .where(
                Video.id == video_id,
                Channel.user_id == user_id,
                Video.status_id == uuid.uuid5(uuid.NAMESPACE_DNS, "video_status:ready"),
            )
        )
        video = result.scalar_one_or_none()
        if not video:
            await self.session.rollback()
            raise VideoNotFoundError()

        # S3 deletion
        video_object_name = str(video.id)
        thumbnail_path = (
            video.thumbnail_path.lstrip("/") if video.thumbnail_path else None
        )

        try:
            await self.s3_client.delete_file(video_object_name, bucket_name="videos")
            if thumbnail_path:
                await self.s3_client.delete_file(
                    thumbnail_path.split("/")[-1], bucket_name="video-thumbnails"
                )
        except Exception as e:
            logging.warning(f"S3 deletion failed for {video_id}: {e}")
            await self.session.rollback()
            raise S3DeletionError()

        # Delete DB record
        await self.session.execute(delete(Video).where(Video.id == video_id))
        await self.session.commit()
        return video
