from fastapi import UploadFile, APIRouter, HTTPException, Query
from typing import List, Literal
from fastapi.responses import StreamingResponse
import logging
from ..schemas.endpoint import FileMeta, UploadResponse, ErrorResponse
from ..services import s3_client
from ..services.rabbit_client import rabbit_broker

router_files = APIRouter(
    prefix="/api/files",
    tags=["files"]
)


# ----- Endpoints -----
@router_files.post(
    "/upload",
    response_model=UploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
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

    try:
        for uploaded_file in uploaded_files:
            uploaded_file.file.seek(0, 2)
            size = uploaded_file.file.tell()
            uploaded_file.file.seek(0)
            logging.info(f"Uploaded file: {uploaded_file.filename} with size: {size}")
            files_meta.append(FileMeta(filename=uploaded_file.filename, size=size))

            logging.info(f"Starting encoding task for file: {uploaded_file.filename}")
            await s3_client.upload_file(uploaded_file.filename, uploaded_file.file)
            await rabbit_broker.publish(uploaded_file.filename, queue="video.encode")

    except Exception as e:
        logging.error(f"Error uploading files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(
        status="accepted",
        files_count=len(uploaded_files),
        files=files_meta
    )


@router_files.get("/download/{filename}")
async def get_file(filename: str,
                   mode: Literal["download", "stream"] = Query("download", description="Streaming mode")):
    """
    Endpoint to stream a file.

    Args:
        filename (str): The name of the file to be streamed.

    Returns:
        StreamingResponse: The file is streamed as a response with the specified media type.
        :param filename:
        :param mode:
    """
    try:
        logging.info(f"Streaming file: {filename}")
        chunk_generator = s3_client.download_file(filename, 1024 * 1024 * 3)
        if mode == "stream":
            headers = {"Content-Disposition": f'inline; filename="{filename}"'}
            logging.info(f"Streaming file: {filename} in streaming mode")
            return StreamingResponse(chunk_generator, media_type="video/mp4", headers=headers)
        else:
            headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
            logging.info(f"Streaming file: {filename} in download mode")
            return StreamingResponse(chunk_generator, media_type="application/octet-stream", headers=headers)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
