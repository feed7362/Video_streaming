from src.core.base_error import AppError
from src.i18n import _


class InvalidFilePathError(AppError):
    code = "INVALID_FILE_PATH"
    status_code = 400

    def __init__(self):
        super().__init__(message=_("Invalid file path format"))


class FileNotFoundS3Error(AppError):
    code = "FILE_NOT_FOUND"
    status_code = 404

    def __init__(self):
        super().__init__(message=_("File not found in storage"))


class SignedUrlGenerationError(AppError):
    code = "SIGNED_URL_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(message=_("Failed to generate signed URL"))


class S3DeletionError(AppError):
    code = "S3_DELETION_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(message=_("Failed to delete files from storage"))


class ResolutionNotFoundError(AppError):
    code = "VIDEO_RESOLUTION_NOT_FOUND"
    status_code = 404

    def __init__(self, resolution: str):
        message = _("Video resolution '%(res)s' not found") % {"res": resolution}
        super().__init__(message=message)


class S3DownloadError(AppError):
    code = "S3_DOWNLOAD_FAILED"
    status_code = 500

    def __init__(self, object_key: str):
        message = _("Failed to download file '%(key)s' from storage") % {
            "key": object_key
        }
        super().__init__(message=message)


class InvalidVideoFormatError(AppError):
    code = "INVALID_VIDEO_FORMAT"
    status_code = 400

    def __init__(self):
        super().__init__(message=_("Invalid video format"))


class InvalidThumbnailFormatError(AppError):
    code = "INVALID_THUMBNAIL_FORMAT"
    status_code = 400

    def __init__(self):
        super().__init__(message=_("Invalid thumbnail format"))


class ChannelNotFoundError(AppError):
    code = "CHANNEL_NOT_FOUND"
    status_code = 404

    def __init__(self):
        super().__init__(message=_("User does not have a channel"))


class VideoUploadFailedError(AppError):
    code = "VIDEO_UPLOAD_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(message=_("Failed to upload video to storage"))


class DuplicateVideoError(AppError):
    code = "DUPLICATE_VIDEO"
    status_code = 409

    def __init__(self):
        super().__init__(message=_("Video with the same hash already exists"))


class JobPublishFailedError(AppError):
    code = "JOB_PUBLISH_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(message=_("Failed to publish encoding job"))
