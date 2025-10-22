import asyncio
import logging
import os
import uuid
from typing import TYPE_CHECKING, List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse

from ..infrastructure import get_s3_client
from ..infrastructure.rabbit_client import get_rabbit_broker
from ..schemas.endpoint import (
    ErrorResponse,
    FileMeta,
    FileStreamResponse,
    SignedUrlResponse,
    UploadResponse,
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
    s3_client: "S3Client" = Depends(get_s3_client),
    broker: "RabbitBroker" = Depends(get_rabbit_broker),
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
    s3_client: "S3Client" = Depends(get_s3_client),
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
            detail=ErrorResponse(message=f"File '{filename}' not found").model_dump(),
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
    s3_client: "S3Client" = Depends(get_s3_client),
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
                detail=ErrorResponse(message=f"File '{path}' not found").model_dump(),
            )
    except Exception as e:
        logging.error(f"Error streaming file: {e}")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=str(e)).model_dump(),
        )

    return SignedUrlResponse(path=path, signed_url=raw_presigned_url, expires_in=3600)
