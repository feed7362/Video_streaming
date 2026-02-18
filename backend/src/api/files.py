from typing import TYPE_CHECKING, Annotated, Literal, Optional
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Query,
    UploadFile,
)
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.background_tasks import deindex_video_in_es
from ..infrastructure import get_async_session, get_rabbit_broker, get_s3_client
from ..infrastructure.elasticsearch import get_es_client
from ..schemas.endpoint import (
    ErrorResponse,
    FileMeta,
    FileResponse,
    FileStreamResponse,
)
from ..schemas.files import SignedUrlResponse
from ..services.auth import get_current_user_id
from ..services.file_signing import FileSigningService
from ..services.files import FileService
from .dependencies.rate_limit import limit_requests

if TYPE_CHECKING:
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
    service = FileService(session, s3_client, broker)

    return await service.upload_video(
        video=video,
        thumbnail=thumbnail,
        name=name,
        description=description,
        privacy=privacy,
        category=category,
        user_id=user_id,
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
            "model": FileStreamResponse,
            "description": "File streaming response.",
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
    """
    Downloads and streams a stored video file.

    Allows a user to download a video file stored in the object storage. The video
    may be requested in its original resolution or a specific resolution as
    available. The response is streamed as a binary file.
    """
    service = FileService(session, s3_client)
    object_key, filename, media_type = await service.get_video_file(
        video_id, user_id, resolution
    )
    chunk_gen = service.stream_file(object_key, bucket_name="videos")

    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(chunk_gen, media_type=media_type, headers=headers)


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
    service = FileService(session, s3_client)
    video = await service.delete_video(video_id, user_id)
    background_tasks.add_task(deindex_video_in_es, str(video_id), es)

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
    file_path: str = Query(..., description="Path to the file to sign"),
    s3_client: "S3Client" = Depends(get_s3_client),
) -> JSONResponse:
    service = FileSigningService(s3_client)
    result = await service.create_signed_url(file_path)

    headers = {"X-Signed-Url": result["signed_url"]}

    return JSONResponse(
        content=SignedUrlResponse(**result).model_dump(),
        headers=headers,
    )
