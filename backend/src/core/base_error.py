class AppError(Exception):
    """Base class for all application-level errors."""

    code: str = "APP_ERROR"
    message: str = "Application error"
    status_code: int = 400

    def __init__(self, message: str | None = None, cause: Exception | None = None):
        if message:
            self.message = message
        if cause:
            self.cause = cause
        super().__init__(self.message)
