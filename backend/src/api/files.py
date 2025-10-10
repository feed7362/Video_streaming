import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response, StreamingResponse

from ..schemas.comments import Comment, CommentPage
from ..schemas.endpoint import ErrorResponse, FileMeta, UploadResponse
from ..schemas.enum import Privacy
from ..schemas.video import VideoPlayback
from ..services import get_s3_client
from ..services.rabbit_client import rabbit_broker

router_files = APIRouter(prefix="/api/video", tags=["files"])


# ----- Endpoints -----
@router_files.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def upload_files(
    uploaded_files: List[UploadFile],
) -> UploadResponse:
    """
    Upload multiple files to S3 asynchronously and trigger encoding tasks in RabbitMQ.
    Returns metadata about uploaded files.
    """
    if not uploaded_files:
        logging.error("No files provided")
        raise HTTPException(status_code=400, detail="No files provided")

    files_meta: List[FileMeta] = []
    s3_client = get_s3_client()
    semaphore = asyncio.Semaphore(5)

    async def upload_single_file(uploaded_file: UploadFile) -> None:
        async with semaphore:
            filename = uploaded_file.filename
            if filename is None:
                raise HTTPException(
                    status_code=400, detail="Uploaded file has no filename"
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
            await rabbit_broker.publish(new_filename, queue="video.encode")

    try:
        tasks = [upload_single_file(f) for f in uploaded_files]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(
        status="accepted", files_count=len(uploaded_files), files=files_meta
    )


@router_files.get("/download/{filename:path}")
async def get_file(filename: str) -> StreamingResponse:
    s3_client = get_s3_client()
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
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    except Exception as e:
        logging.error(f"Error downloading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_files.get("/sign_url")
async def sign_object(path: str) -> Response:
    s3_client = get_s3_client()
    path = path.replace("/minio/videos/", "")
    try:
        raw_presigned_url = await s3_client.generate_presigned_url(
            path, "get_object", expires_in=3600, bucket_name="videos"
        )
        if raw_presigned_url is None:
            logging.error(f"File '{path}' not found or URL could not be generated")
            raise HTTPException(status_code=404, detail=f"File '{path}' not found")
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return Response(status_code=200, headers={"X-Signed-Url": raw_presigned_url})


@router_files.get("/info/{video_id}", response_model=VideoPlayback)
async def get_video_info(video_id: str) -> VideoPlayback:
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
        raise HTTPException(status_code=500, detail=str(e))


@router_files.get("/comments/{video_id}", response_model=CommentPage)
async def get_comments(video_id: str, page: int = 1, size: int = 20) -> CommentPage:
    total = 53
    comments = [
        Comment(
            id=uuid.UUID(),
            video_id=uuid.UUID(video_id),
            created_at=datetime.now(),
            author=f"User {i}",
            text=f"Comment {i}",
        )
        for i in range((page - 1) * size, min(page * size, total))
    ]
    return CommentPage(items=comments, page=page, size=size, total=total)
