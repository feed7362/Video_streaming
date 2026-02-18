from src.core.base_error import AppError


class VideoSearchError(AppError):
    code = "VIDEO_SEARCH_FAILED"
    status_code = 500

    def __init__(self, query: str, cause: Exception | None = None):
        message = f"Failed to perform search for query: '{query}'"
        super().__init__(message=message, cause=cause)


class VideoHintsError(AppError):
    code = "VIDEO_HINTS_FAILED"
    status_code = 500

    def __init__(self, query: str, cause: Exception | None = None):
        message = f"Failed to fetch video hints for query: '{query}'"
        super().__init__(message=message, cause=cause)
