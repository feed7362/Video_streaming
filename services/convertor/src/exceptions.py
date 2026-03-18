class AppError(Exception):
    """Base class for all application-level errors."""

    code: str = "APP_ERROR"
    message: str = "Application error"

    def __init__(self, message: str | None = None, cause: Exception | None = None):
        if message:
            self.message = message
        if cause:
            self.cause = cause
        super().__init__(self.message)


class DirectoryPrepareError(AppError):
    code = "DIR_PREPARE_FAILED"

    def __init__(self, video_id: str):
        super().__init__(f"Failed to prepare local directories for video '{video_id}'")


class DirectoryCleanupError(AppError):
    code = "DIR_CLEANUP_FAILED"

    def __init__(self, video_id: str):
        super().__init__(f"Failed to cleanup local directories for video '{video_id}'")


class GPUNoAvailableError(AppError):
    code = "GPU_NOT_AVAILABLE"

    def __init__(self):
        super().__init__("CUDA GPU not available on this worker")


class FFmpegError(AppError):
    code = "FFMPEG_ERROR"


class FFmpegStartError(FFmpegError):
    code = "FFMPEG_START_FAILED"

    def __init__(self):
        super().__init__("Failed to start ffmpeg process")


class FFmpegInputError(FFmpegError):
    code = "FFMPEG_INPUT_FAILED"

    def __init__(self):
        super().__init__("Error while streaming input to ffmpeg")


class FFmpegExecutionError(FFmpegError):
    code = "FFMPEG_EXECUTION_FAILED"

    def __init__(self, return_code: int, stderr: str | None = None):
        msg = f"ffmpeg exited with code {return_code}"
        if stderr:
            msg = f"{msg}: {stderr}"
        super().__init__(msg)
        self.return_code = return_code


class FFProbeError(AppError):
    code = "FFPROBE_FAILED"

    def __init__(self, details: str | None = None):
        msg = "Failed to probe input media"
        if details:
            msg = f"{msg}: {details}"
        super().__init__(msg)


class InvalidMediaError(AppError):
    code = "INVALID_MEDIA"

    def __init__(self, reason: str):
        super().__init__(f"Invalid media input: {reason}")
