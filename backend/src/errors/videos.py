from src.core.base_error import AppError


class VideoNotFoundError(AppError):
    code = "VIDEO_NOT_FOUND"
    message = "Video not found or not owned by the user"
    status_code = 404


class VideoPrivacyUpdateForbidden(AppError):
    code = "VIDEO_PRIVACY_FORBIDDEN"
    status_code = 403
    message = "You do not own this video"


class VideoViewRecordError(AppError):
    code = "VIDEO_VIEW_RECORD_FAILED"
    status_code = 500
    message = "Failed to record video view"


class InvalidPrivacyError(AppError):
    code = "PRIVACY_LEVEL_NOT_FOUND"
    status_code = 400

    def __init__(self, privacy_level: str):
        super().__init__(f"Invalid privacy level: {privacy_level}")
