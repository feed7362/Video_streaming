from src.core.base_error import AppError


class UnknownEncoderStatusError(AppError):
    code = "UNKNOWN_ENCODER_STATUS"
    status_code = 400

    def __init__(self, status: str):
        super().__init__(f"Unknown encoder status: {status}")


class VideoEncodingPersistenceError(AppError):
    code = "VIDEO_ENCODING_PERSISTENCE_FAILED"
    status_code = 500
    message = "Failed to persist video encoding results"


class ResolutionInsertError(AppError):
    code = "RESOLUTION_INSERT_FAILED"
    status_code = 500
    message = "Failed to insert resolutions"
