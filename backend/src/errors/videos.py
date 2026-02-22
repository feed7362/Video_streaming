from src.core.base_error import AppError
from src.i18n import _


class VideoNotFoundError(AppError):
    code = "VIDEO_NOT_FOUND"
    status_code = 404

    def __init__(self):
        super().__init__(_("Video not found or not owned by the user"))


class VideoPrivacyUpdateForbidden(AppError):
    code = "VIDEO_PRIVACY_FORBIDDEN"
    status_code = 403

    def __init__(self):
        super().__init__(_("You do not own this video"))


class VideoViewRecordError(AppError):
    code = "VIDEO_VIEW_RECORD_FAILED"
    status_code = 500

    def __init__(self):
        super().__init__(_("Failed to record video view"))


class InvalidPrivacyError(AppError):
    code = "PRIVACY_LEVEL_NOT_FOUND"
    status_code = 400

    def __init__(self, privacy_level: str):
        super().__init__(
            _("Invalid privacy level: %(level)s") % {"level": privacy_level}
        )
