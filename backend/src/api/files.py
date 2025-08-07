from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from fastapi import APIRouter

router_files = APIRouter(
    prefix="/api/files",
    tags=["files"]
)


@router_files.post("/upload/single")
async def upload_file(uploaded_file: UploadFile):
    """
        Endpoint to upload a single file.

        Args:
            uploaded_file (UploadFile): The file to be uploaded, provided in the request.

        Returns:
            None: The file is saved locally with a prefix "1_" added to its original filename.
        """
    file = uploaded_file.file
    filename = uploaded_file.filename
    with open(f"1_{filename}", "wb") as f:
        f.write(file.read())


@router_files.post("/upload/multiple")
async def upload_files(uploaded_files: list[UploadFile]):
    """
    Endpoint to upload multiple files.

    Args:
        uploaded_files (list[UploadFile]): A list of files to be uploaded, provided in the request.

    Returns:
        None: Each file is saved locally with a prefix "1_" added to its original filename.
    """
    for uploaded_file in uploaded_files:
        file = uploaded_file.file
        filename = uploaded_file.filename
        with open(f"1_{filename}", "wb") as f:
            f.write(file.read())


@router_files.get("/download/{filename}")
async def get_file(filename: str):
    """
    Endpoint to retrieve a file.

    Args:
        filename (str): The name of the file to be retrieved.

    Returns:
        FileResponse: The file is returned as a response.
    """
    return FileResponse(filename)  # Return the file as a response.


def interfile(filename: str):
    """
    Generator function to read a file in chunks.

    Args:
        filename (str): The name of the file to be read.

    Yields:
        bytes: A chunk of the file's content.
    """
    with open(filename, "rb") as file:
        while chunk := file.read(1024 * 1024):  # Read the file in chunks of 1 MB.
            yield chunk


@router_files.get("/streaming/{filename}")
async def get_streaming_file(filename: str):
    """
    Endpoint to stream a file.

    Args:
        filename (str): The name of the file to be streamed.

    Returns:
        StreamingResponse: The file is streamed as a response with the specified media type.
    """
    return StreamingResponse(interfile(filename), media_type="video/mp4")
