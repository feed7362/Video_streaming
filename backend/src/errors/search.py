from src.core.base_error import AppError
from src.i18n import _


class VideoSearchError(AppError):
    code = "VIDEO_SEARCH_FAILED"
    status_code = 500

    def __init__(self, query: str, cause: Exception | None = None):
        message = _("Failed to perform search for query: '%(query)s'") % {
            "query": query
        }
        super().__init__(message=message, cause=cause)


class VideoHintsError(AppError):
    code = "VIDEO_HINTS_FAILED"
    status_code = 500

    def __init__(self, query: str, cause: Exception | None = None):
        message = _("Failed to perform search hints for query: '%(query)s'") % {
            "query": query
        }
        super().__init__(message=message, cause=cause)
