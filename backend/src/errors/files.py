from src.core.base_error import AppError
from src.i18n import _


class InvalidFilePathError(AppError):
    code = "INVALID_FILE_PATH"
    status_code = 400

    def __init__(self):
        super().__init__(_("Invalid file path format"))


class FileNotFoundS3Error(AppError):
    code = "FILE_NOT_FOUND"
    status_code = 404

    def __init__(self):
        super().__init__(_("File not found in storage"))


class SignedUrlGenerationError(AppError):
    code = "SIGNED_URL_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(_("Failed to generate signed URL"))


class S3DeletionError(AppError):
    code = "S3_DELETION_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(_("Failed to delete files from storage"))


class ResolutionNotFoundError(AppError):
    code = "VIDEO_RESOLUTION_NOT_FOUND"
    status_code = 404

    def __init__(self, resolution: str):
        super().__init__(
            _("Video resolution '%(res)s' not found") % {"res": resolution}
        )


class S3DownloadError(AppError):
    code = "S3_DOWNLOAD_FAILED"
    status_code = 500

    def __init__(self, object_key: str):
        super().__init__(
            _("Failed to download file '%(key)s' from storage") % {"key": object_key}
        )


class InvalidVideoFormatError(AppError):
    code = "INVALID_VIDEO_FORMAT"
    status_code = 400

    def __init__(self):
        super().__init__(_("Invalid video format"))


class InvalidThumbnailFormatError(AppError):
    code = "INVALID_THUMBNAIL_FORMAT"
    status_code = 400

    def __init__(self):
        super().__init__(_("Invalid thumbnail format"))


class ChannelNotFoundError(AppError):
    code = "CHANNEL_NOT_FOUND"
    status_code = 404

    def __init__(self):
        super().__init__(_("User does not have a channel"))


class VideoUploadFailedError(AppError):
    code = "VIDEO_UPLOAD_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(_("Failed to upload video to storage"))


class DuplicateVideoError(AppError):
    code = "DUPLICATE_VIDEO"
    status_code = 409

    def __init__(self):
        super().__init__(_("Video with the same hash already exists"))


class JobPublishFailedError(AppError):
    code = "JOB_PUBLISH_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(_("Failed to publish encoding job"))


class FileTooLargeError(AppError):
    code = "FILE_TOO_LARGE"
    status_code = 400

    def __init__(self, file_size: int):
        super().__init__(
            _("The uploaded file exceeds " "the maximum allowed size of %(size)sMB")
            % {"size": file_size}
        )


class EmptyFileError(AppError):
    code = "EMPTY_FILE"
    status_code = 400

    def __init__(self):
        super().__init__(_("The uploaded file is empty"))
