from __future__ import annotations

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.pagination import paginate_query
from ..infrastructure import get_s3_client
from ..infrastructure.database import get_async_session
from ..infrastructure.rabbit_client import get_rabbit_broker
from ..models import Video
from ..models.comments import Comment
from ..schemas.comments import CommentPage
from ..schemas.endpoint import (
    APIError,
    ErrorResponse,
    FileMeta,
    FileStreamResponse,
    SignedUrlResponse,
    UploadResponse,
)
from ..schemas.enum import Privacy
from ..schemas.video import VideoPage, VideoPlayback

if TYPE_CHECKING:  # pragma: no cover - used only for type checkers
    from faststream.rabbit import RabbitBroker

    from ..infrastructure.s3_client import S3Client

router_files = APIRouter(
    prefix="/api/video",
    tags=["files"],
    default_response_class=JSONResponse,
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"},
    },
)


# ----- Endpoints -----
@router_files.post(
    "/upload",
    response_model=UploadResponse,
    summary="Upload video files",
    description="Uploads one or more video files to object storage and schedules encoding jobs.",
    response_description="Metadata describing the uploaded files.",
    responses={
        200: {
            "model": UploadResponse,
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
    uploaded_files: List[UploadFile],
    s3_client: S3Client = Depends(get_s3_client),
    broker: RabbitBroker = Depends(get_rabbit_broker),
) -> UploadResponse:
    """
    Upload multiple files to S3 asynchronously and trigger encoding tasks in RabbitMQ.
    Returns metadata about uploaded files.
    """
    if not uploaded_files:
        logging.error("No files provided")
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(message="No files provided").model_dump(),
        )

    files_meta: List[FileMeta] = []
    semaphore = asyncio.Semaphore(5)

    async def upload_single_file(uploaded_file: UploadFile) -> None:
        async with semaphore:
            filename = uploaded_file.filename
            if filename is None:
                raise HTTPException(
                    status_code=400,
                    detail=ErrorResponse(
                        message="Uploaded file is missing a filename."
                    ).model_dump(),
                )
            ext = os.path.splitext(filename)[-1]
            new_filename = f"{str(uuid.uuid4())}{ext}"
            uploaded_file.file.seek(0, 2)
            size = uploaded_file.file.tell()
            uploaded_file.file.seek(0)
            logging.info(f"Uploaded file: {new_filename} with size: {size}")
            files_meta.append(FileMeta(filename=new_filename, size=size))

            logging.info(f"Starting encoding task for file: {new_filename}")
            await s3_client.upload_file(
                new_filename, uploaded_file.file, bucket_name="videos"
            )
            await broker.publish(new_filename, queue="video.encode")

    try:
        tasks = [upload_single_file(f) for f in uploaded_files]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )

    return UploadResponse(
        status="accepted", files_count=len(uploaded_files), files=files_meta
    )


@router_files.get(
    "/download/{filename:path}",
    response_model=FileStreamResponse,
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
    filename: str = Path(..., description="Full path of the file to download."),
    s3_client: S3Client = Depends(get_s3_client),
) -> StreamingResponse:
    try:
        logging.info(f"Downloading file: {filename}")
        chunk_generator = s3_client.download_file(
            filename, 1024 * 1024 * 3, bucket_name="videos"
        )
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(
            chunk_generator, media_type="application/octet-stream", headers=headers
        )
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found")
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                message=f"File '{filename}' not found"
            ).model_dump(),
        )
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
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
    path: str = Query(
        ..., description="Path to the file within the videos bucket to sign."
    ),
    s3_client: S3Client = Depends(get_s3_client),
) -> SignedUrlResponse:
    path = path.replace("/minio/videos/", "")
    try:
        raw_presigned_url = await s3_client.generate_presigned_url(
            path, "get_object", expires_in=3600, bucket_name="videos"
        )
        if raw_presigned_url is None:
            logging.error(f"File '{path}' not found or URL could not be generated")
            raise HTTPException(
                status_code=404,
                detail=ErrorResponse(
                    message=f"File '{path}' not found"
                ).model_dump(),
            )
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )

    return SignedUrlResponse(path=path, signed_url=raw_presigned_url, expires_in=3600)


@router_files.get(
    "/info/{video_id}",
    response_model=VideoPlayback,
    summary="Get video playback information",
    description="Retrieves metadata and playback details for a specific video.",
    response_description="Metadata describing the requested video.",
    responses={
        200: {
            "model": VideoPlayback,
            "description": "Video metadata retrieved successfully.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Video metadata could not be found.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while retrieving metadata.",
        },
    },
)
async def get_video_info(
    video_id: str = Path(..., description="UUID of the video to retrieve playback info for."),
) -> VideoPlayback:
    channel_name = "Channel Name"
    s3_video = f"{video_id}/master.m3u8"
    s3_thumbnail = f"{video_id}/thumbnail.jpg"
    s3_channel_avatar = f"{channel_name}/avatar.jpg"
    try:
        logging.info(f"Streaming playlist master: {video_id}")
        return VideoPlayback(
            id=uuid.UUID(video_id),
            name="test.mp4",
            description="Test Description",
            created_at=datetime.now(),
            master_hls_url=f"/minio/videos/{s3_video}",
            privacy=Privacy.PUBLIC,
            resolutions=["360p", "720p"],
            channel_name="Channel Name",
            likes_count=123,
            views_count=111,
            dislikes_count=22,
            thumbnail_url=f"/minio/thumbnail/{s3_thumbnail}",
            avatar_url=f"/minio/avatar/{s3_channel_avatar}",
        )
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )


@router_files.get(
    "/comments/{video_id}",
    response_model=CommentPage,
    summary="List comments for a video",
    description="Returns a paginated list of comments belonging to the specified video.",
    response_description="Paginated comment list.",
    responses={
        200: {
            "model": CommentPage,
            "description": "Comments retrieved successfully.",
        },
        400: {
            "model": APIError,
            "description": "Invalid pagination parameters provided.",
        },
        404: {
            "model": ErrorResponse,
            "description": "Video not found or has no comments.",
        },
        500: {
            "model": ErrorResponse,
            "description": "Unexpected error occurred while retrieving comments.",
        },
    },
)
async def get_comments(
    video_id: uuid.UUID = Path(..., description="UUID of the video whose comments are requested."),
    page: int = Query(1, ge=1, description="Page number for paginated results."),
    size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of comments to include per page (1-100).",
    ),
    session: AsyncSession = Depends(get_async_session),
) -> CommentPage:
    filters = [Comment.video_id == video_id]

    comments, total = await paginate_query(
        session=session,
        model=Comment,
        page=page,
        size=size,
        filters=filters,
        order_by=Comment.created_at.desc(),
    )

    return CommentPage(items=comments, page=page, size=size, total=total)


@router_files.get(
    "/videos",
    response_model=VideoPage,
    summary="List all videos",
    description="Returns a paginated list of videos with metadata such as title, duration, and status.",
    response_description="A paginated list of videos.",
    responses={
        200: {
            "model": VideoPage,
            "description": "List of videos successfully retrieved.",
        },
        400: {
            "model": APIError,
            "description": "Invalid query parameters (e.g., invalid page/size).",
        },
        500: {
            "model": APIError,
            "description": "Internal server error.",
        },
    },
)
async def get_videos(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    session: AsyncSession = Depends(get_async_session),
) -> VideoPage:
    videos, total = await paginate_query(
        session=session,
        model=Video,
        page=page,
        size=size,
        order_by=Video.created_at.desc(),
    )
    return VideoPage(items=videos, page=page, size=size, total=total)
