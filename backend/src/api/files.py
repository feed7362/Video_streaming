import asyncio
import logging
from typing import List

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from ..schemas.endpoint import ErrorResponse, FileMeta, UploadResponse
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
            uploaded_file.file.seek(0, 2)
            size = uploaded_file.file.tell()
            uploaded_file.file.seek(0)
            logging.info(f"Uploaded file: {uploaded_file.filename} with size: {size}")
            files_meta.append(FileMeta(filename=uploaded_file.filename, size=size))

            logging.info(f"Starting encoding task for file: {uploaded_file.filename}")
            await s3_client.upload_file(uploaded_file.filename, uploaded_file.file)
            await rabbit_broker.publish(uploaded_file.filename, queue="video.encode")

    try:
        tasks = [upload_single_file(f) for f in uploaded_files]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(
        status="accepted", files_count=len(uploaded_files), files=files_meta
    )


@router_files.get("/streaming/{filename:path}")
async def stream_video(filename: str) -> str:
    s3_client = get_s3_client()
    try:
        logging.info(f"Streaming file: {filename}")
        presigned_url = await s3_client.generate_presigned_url(filename, "get_object")
        if presigned_url is None:
            logging.error(f"File '{filename}' not found or URL could not be generated")
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
        return presigned_url
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router_files.get("/download/{filename:path}")
async def get_file(filename: str) -> StreamingResponse:
    s3_client = get_s3_client()
    try:
        logging.info(f"Downloading file: {filename}")
        chunk_generator = s3_client.download_file(filename, 1024 * 1024 * 3)
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
