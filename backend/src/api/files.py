import logging
import re
from pathlib import Path as FilePath
from typing import TYPE_CHECKING, Annotated, Literal, Optional
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

import xxhash
from elasticsearch import AsyncElasticsearch
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.auth import get_current_user_id
from ..core.background_tasks import deindex_video_in_es
from ..core.dependecies import limit_requests
from ..infrastructure import get_async_session, get_rabbit_broker, get_s3_client
from ..infrastructure.elasticsearch import get_es_client
from ..models import Channel, Video, VideoResolution
from ..schemas.endpoint import (
    ErrorResponse,
    FileMeta,
    FileResponse,
    FileStreamResponse,
    SignedUrlResponse,
)

if TYPE_CHECKING:  # pragma: no cover - used only for type checkers
    from faststream.rabbit import RabbitBroker

    from ..infrastructure.s3_client import S3Client

router_files = APIRouter(
    prefix="/api/files",
    tags=["files"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


# ----- Endpoints -----
@router_files.post(
    "/upload_video",
    response_model=FileResponse,
    dependencies=[
        Depends(limit_requests("upload_video", max_requests=5, window_seconds=60))
    ],
    summary="Upload video files",
    description="Uploads one or more video files to object storage and schedules encoding jobs.",
    response_description="Metadata describing the uploaded files.",
    responses={
        200: {
            "model": FileResponse,
            "description": "Files successfully uploaded and encoding queued.",
        },
        400: {
            "model": ErrorResponse,
            "description": "Request did not include any files or contained invalid data.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while uploading or scheduling encoding.",
        },
    },
)
async def upload_files(
    video: Annotated[UploadFile, File(description="A video file to upload")],
    thumbnail: Annotated[
        Optional[UploadFile], File(description="Preview image for the video")
    ],
    name: str = Query(..., description="Name of the uploaded files."),
    description: str = Query(..., description="Description of the uploaded files."),
    privacy: Literal["public", "private"] = Query(
        default="public",
        description="Privacy level: `public` (visible to all) or `private` (owner only)",
    ),
    category: Literal[
        "education",
        "entertainment",
        "music",
        "gaming",
        "technology",
        "science",
        "movies",
        "sports",
        "news",
        "travel",
        "lifestyle",
        "fashion",
        "health & fitness",
        "food & cooking",
        "comedy",
        "documentary",
        "art & design",
        "business & finance",
        "animals & nature",
        "automotive",
        "history",
        "podcasts",
        "shorts",
    ] = Query(default="entertainment", description="Category of the uploaded files."),
    user_id: UUID = Depends(get_current_user_id),
    s3_client: "S3Client" = Depends(get_s3_client),
    session: AsyncSession = Depends(get_async_session),
    broker: "RabbitBroker" = Depends(get_rabbit_broker),
) -> FileResponse:
    """
    Upload multiple files to S3 asynchronously and trigger encoding tasks in RabbitMQ.
    Returns metadata about uploaded files.
    """
    if video is None or not (video.content_type or "").startswith("video/"):
        raise HTTPException(400, "Invalid video format")

    if thumbnail and not (thumbnail.content_type or "").startswith("image/"):
        raise HTTPException(400, "Invalid image format")

    async def compute_hash_and_size(uploaded_file: UploadFile) -> tuple[str, int]:
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

    try:
        # ---- Video ----
        video_hash, video_size = await compute_hash_and_size(video)
        video_id = uuid4()

        channel = await session.execute(
            select(Channel.id).where(Channel.user_id == user_id)
        )
        channel_id = channel.scalar_one_or_none()

        if channel_id is None:
            raise HTTPException(400, "User does not have a channel")

        result = await session.execute(
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
        await session.commit()

        if inserted_id is None:
            logging.info(f"Hash duplicate: {video_hash}")
            existing = await session.execute(
                select(Video).where(Video.hash == video_hash)
            )
            existing_video = existing.scalar_one_or_none()
            await session.commit()

            if existing_video is None:
                raise HTTPException(
                    500, "Duplicate video hash found but no record exists"
                )

            return FileResponse(
                status="duplicate",
                files=[
                    FileMeta(
                        file_id=existing_video.id,
                        filename=existing_video.name,
                        size=existing_video.size,
                    )
                ],
            )

        # ---- Thumbnail ----
        if thumbnail:
            thumb_suffix = FilePath(thumbnail.filename or "").suffix
            thumbnail_id = str(uuid4())
            thumb_name = f"{thumbnail_id}{thumb_suffix}"
            await s3_client.upload_file(
                thumb_name, thumbnail.file, bucket_name="video-thumbnails"
            )
            await session.execute(
                update(Video)
                .where(Video.id == video_id)
                .values(thumbnail_path=f"/minio/video-thumbnails/{thumb_name}")
            )
            await session.commit()

        # ----- Upload video to S3 -----
        try:
            video_suffix = FilePath(video.filename or "").suffix
            new_filename = f"{video_id}{video_suffix}"
            await s3_client.upload_file(new_filename, video.file, bucket_name="videos")
        except Exception as e:
            logging.error(f"S3 upload failed. Removing Video row {video_id}: {e}")
            await session.execute(delete(Video).where(Video.id == video_id))
            await session.commit()
            raise HTTPException(500, "Failed to upload video to storage")

        # ----- Publish job -----
        await broker.publish(new_filename, queue="video.encode", priority=10)

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
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )


@router_files.get(
    "/download_video",
    response_model=FileStreamResponse,
    dependencies=[
        Depends(limit_requests("download_video", max_requests=5, window_seconds=60))
    ],
    summary="Download a stored video file",
    description="Streams a video file stored in object storage as a binary response.",
    response_description="Binary stream of the requested file.",
    responses={
        200: {
            "description": "File streaming response.",
            "content": {
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"}
                }
            },
        },
        404: {
            "model": ErrorResponse,
            "description": "Requested file was not found.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while retrieving the file.",
        },
    },
)
async def get_file(
    video_id: UUID = Query(..., description="UUID of the video to delete."),
    resolution: Optional[str] = Query(
        None,
        description="Specific resolution to download (e.g., '360p', '720p', '1080p')."
        " If omitted, original file is returned.",
    ),
    user_id: UUID = Depends(get_current_user_id),
    s3_client: "S3Client" = Depends(get_s3_client),
    session: AsyncSession = Depends(get_async_session),
) -> StreamingResponse:
    try:
        result = await session.execute(
            select(Video)
            .join(Channel, Channel.id == Video.channel_id)
            .where(Video.id == video_id, Channel.user_id == user_id)
        )
        video = result.scalar_one_or_none()

        if video is None:
            raise HTTPException(
                404, f"Video with ID {video_id} not found or not owned by the user."
            )

        if resolution:
            target_height = int(resolution.rstrip("p"))
            # Attempt to find a matching encoded resolution (e.g., 720p)
            result = await session.execute(
                select(VideoResolution).where(
                    (VideoResolution.video_id == video_id)
                    & (VideoResolution.height == target_height)
                )
            )
            res_obj = result.scalar_one_or_none()

            if res_obj:
                object_key = res_obj.playlist_path.lstrip("/")
                filename = f"{video.name}_{res_obj.height}p.m3u8"
                media_type = "application/vnd.apple.mpegurl"
            else:
                raise HTTPException(
                    status_code=404,
                    detail=ErrorResponse(
                        message=f"Resolution '{resolution}' not found for this video."
                    ).model_dump(),
                )

        logging.info(f"Downloading file with video id: {video_id}")
        chunk_generator = s3_client.download_file(
            object_key, 1024 * 1024 * 3, bucket_name="videos"
        )
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            chunk_generator, media_type=media_type, headers=headers
        )
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found")
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(message=f"File '{filename}' not found").model_dump(),
        )
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )


@router_files.delete(
    "/delete_video",
    response_model=FileResponse,
    dependencies=[
        Depends(limit_requests("delete_video", max_requests=5, window_seconds=60))
    ],
    summary="Delete a video and its assets",
    description=(
        "Deletes a video entry from the database and removes all its related files "
        "(HLS streams, thumbnails) from object storage."
    ),
    responses={
        200: {"model": FileResponse, "description": "Video successfully deleted."},
        400: {
            "model": ErrorResponse,
            "description": "Invalid request or unauthorized.",
        },
        404: {"model": ErrorResponse, "description": "Video not found."},
        500: {"model": ErrorResponse, "description": "Unexpected server error."},
    },
)
async def delete_files(
    background_tasks: BackgroundTasks,
    video_id: UUID = Query(..., description="UUID of the video to delete."),
    user_id: UUID = Depends(get_current_user_id),
    s3_client: "S3Client" = Depends(get_s3_client),
    session: AsyncSession = Depends(get_async_session),
    es: "AsyncElasticsearch" = Depends(get_es_client),
) -> FileResponse:
    """
    Delete a video, its database record, and all associated storage files.
    """
    try:
        result = await session.execute(
            select(Video)
            .join(Channel, Channel.id == Video.channel_id)
            .where(
                Video.id == video_id,
                Channel.user_id == user_id,
                Video.status_id == uuid5(NAMESPACE_DNS, "video_status:ready"),
            )
        )
        video = result.scalar_one_or_none()

        if video is None:
            raise HTTPException(
                404, f"Video with ID {video_id} not found or not owned by the user."
            )

        # ---- Derive filenames to remove from S3 ----
        video_object_name = f"{video.id}"  # or f"{video.id}.mp4" depending on naming
        hls_prefix = f"{video.id}/"  # where your encoded HLS segments live
        thumbnail_path = (
            video.thumbnail_path.lstrip("/") if video.thumbnail_path else None
        )

        # ---- Delete video and thumbnails from object storage ----
        try:
            await s3_client.delete_prefix(hls_prefix, bucket_name="videos")
            # Delete original uploaded file
            await s3_client.delete_file(video_object_name, bucket_name="videos")

            # Delete thumbnail if exists
            if thumbnail_path:
                await s3_client.delete_file(
                    thumbnail_path.split("/")[-1], bucket_name="video-thumbnails"
                )

        except Exception as s3_err:
            logging.warning(f"Failed to remove S3 files for video {video_id}: {s3_err}")

        # ---- Delete record from a database ----
        await session.execute(delete(Video).where(Video.id == video_id))
        await session.commit()

        logging.info(f"Video {video_id} deleted successfully by user {user_id}")

        background_tasks.add_task(deindex_video_in_es, str(video_id), es)
        logging.info(f"Deindexed video {video_id} from ES")

        return FileResponse(
            status="deleted",
            files=[
                FileMeta(
                    file_id=video_id,
                    filename=video.name,
                    size=video.size,
                )
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        logging.error(f"Error deleting video {video_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )


@router_files.get(
    "/sign_url",
    response_model=SignedUrlResponse,
    summary="Create a signed URL",
    description=(
        "Generates a pre-signed URL that allows temporary access to a video file "
        "stored in object storage."
    ),
    response_description="Signed URL metadata for accessing the requested file.",
    responses={
        200: {
            "model": SignedUrlResponse,
            "description": "Pre-signed URL generated successfully.",
        },
        404: {
            "model": ErrorResponse,
            "description": "The requested file could not be found in storage.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while generating the signed URL.",
        },
    },
)
async def sign_object(
    file_path: str = Query(
        ..., description="Path to the file within the videos bucket to sign."
    ),
    s3_client: "S3Client" = Depends(get_s3_client),
) -> JSONResponse:
    match = re.match(r"^/minio/([^/]+)/(.*)$", file_path)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid file path format")
    bucket_name, object_key = match.groups()
    logging.info(f"Generating signed URL for file {object_key} in bucket {bucket_name}")
    try:
        raw_presigned_url = await s3_client.generate_presigned_url(
            object_key, "get_object", expires_in=3600, bucket_name=bucket_name
        )
        if raw_presigned_url is None:
            logging.error(
                f"File '{object_key}' on bucket {bucket_name} not found or URL could not be generated"
            )
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    message=f"File '{object_key}' on bucket {bucket_name} not found"
                ).model_dump(),
            )
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )

    payload = SignedUrlResponse(
        path=object_key,
        signed_url=raw_presigned_url,
        expires_in=3600,
    )
    headers = {"X-Signed-Url": raw_presigned_url}
    return JSONResponse(content=payload.model_dump(), headers=headers)
