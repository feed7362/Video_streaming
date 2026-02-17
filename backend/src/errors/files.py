from src.core.base_error import AppError


class InvalidFilePathError(AppError):
    code = "INVALID_FILE_PATH"
    message = "Invalid file path format"
    status_code = 400


class FileNotFoundS3Error(AppError):
    code = "FILE_NOT_FOUND"
    message = "File not found in storage"
    status_code = 404


class SignedUrlGenerationError(AppError):
    code = "SIGNED_URL_FAILED"
    message = "Failed to generate signed URL"
    status_code = 500


class VideoNotFoundError(AppError):
    code = "VIDEO_NOT_FOUND"
    message = "Video not found or not owned by the user"
    status_code = 404


class S3DeletionError(AppError):
    code = "S3_DELETION_FAILED"
    message = "Failed to delete files from storage"
    status_code = 500


class ResolutionNotFoundError(AppError):
    code = "VIDEO_RESOLUTION_NOT_FOUND"
    status_code = 404

    def __init__(self, resolution: str):
        self.message = f"Video resolution '{resolution}' not found"
        super().__init__(self.message)


class S3DownloadError(AppError):
    code = "S3_DOWNLOAD_FAILED"
    status_code = 500

    def __init__(self, object_key: str):
        self.message = f"Failed to download file '{object_key}' from storage"
        super().__init__(self.message)


class InvalidVideoFormatError(AppError):
    code = "INVALID_VIDEO_FORMAT"
    message = "Invalid video format"
    status_code = 400


class InvalidThumbnailFormatError(AppError):
    code = "INVALID_THUMBNAIL_FORMAT"
    message = "Invalid thumbnail format"
    status_code = 400


class ChannelNotFoundError(AppError):
    code = "CHANNEL_NOT_FOUND"
    message = "User does not have a channel"
    status_code = 404


class VideoUploadFailedError(AppError):
    code = "VIDEO_UPLOAD_FAILED"
    message = "Failed to upload video to storage"
    status_code = 500


class DuplicateVideoError(AppError):
    code = "DUPLICATE_VIDEO"
    message = "Video with the same hash already exists"
    status_code = 409


class JobPublishFailedError(AppError):
    code = "JOB_PUBLISH_FAILED"
    message = "Failed to publish encoding job"
    status_code = 500
