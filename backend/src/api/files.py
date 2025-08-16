from fastapi import UploadFile, APIRouter
from typing import List, Optional, Dict
from fastapi.responses import StreamingResponse

from ..services import s3_client
from ..services.rabbit_client import rabbit_broker

router_files = APIRouter(
    prefix="/api/files",
    tags=["files"]
)


@router_files.post("/upload")
async def upload_files(uploaded_files: List[UploadFile]) -> Dict:
    """
    Endpoint to upload multiple files to an S3 bucket.

    Args:
        uploaded_files (Optional[List[UploadFile]]): A list of files to be uploaded.
            If no files are provided, the list can be None.

    Returns:
        Dict: A dictionary containing the status of the upload operation.
            If successful, it includes the number of files uploaded.
            If an error occurs, it includes the error message.
    """
    try:
        for uploaded_file in uploaded_files:
            await s3_client.upload_file(uploaded_file.filename, uploaded_file.file)
            await rabbit_broker.publish(uploaded_file.filename, queue="video.encode")
    except Exception as e:
        return {"status": "error", "message": str(e)}
    return {"status": "uploaded", "files_count": len(uploaded_files)}


# @router_files.get("/download/{filename}")
# async def get_file(filename: str):
#     """
#     Endpoint to retrieve a file.
#
#     Args:
#         filename (str): The name of the file to be retrieved.
#
#     Returns:
#         FileResponse: The file is returned as a response.
#     """
#     file = await s3_client.download_file(filename)
#     return FileResponse(file)  # Return the file as a response.


def interfile(filename: str):
    """
    Generator function to read a file in chunks.

    Args:
        filename (str): The name of the file to be read.

    Yields:
        bytes: A chunk of the file's content.
    """
    with open(filename, "rb") as file:
        while chunk := file.read(1024 * 1024 * 3):  # Read the file in chunks of 3 MB.
            yield chunk


@router_files.get("/streaming/{filename}")
async def get_streaming_file(filename: str, mode: str = "download"):
    """
    Endpoint to stream a file.

    Args:
        filename (str): The name of the file to be streamed.

    Returns:
        StreamingResponse: The file is streamed as a response with the specified media type.
    """
    await s3_client.download_file(filename, 1024 * 1024 * 3)
    if mode == "stream":
        headers = {"Content-Disposition": f'inline; filename="{filename}"'}
        return StreamingResponse(interfile(filename), media_type="video/mp4", headers=headers)
    else:
        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return StreamingResponse(interfile(filename), media_type="application/octet-stream", headers=headers)
