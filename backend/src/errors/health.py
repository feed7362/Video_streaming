from src.core.base_error import AppError
from src.i18n import _


class DatabaseUnavailableError(AppError):
    code = "DATABASE_UNAVAILABLE"
    status_code = 503

    def __init__(self, cause: Exception | None = None):
        super().__init__(_("Database is unavailable"), cause=cause)


class ObjectStorageUnavailableError(AppError):
    code = "OBJECT_STORAGE_UNAVAILABLE"
    status_code = 503

    def __init__(self, cause: Exception | None = None):
        super().__init__(_("Object storage is not reachable"), cause=cause)


class MessageBrokerUnavailableError(AppError):
    code = "MESSAGE_BROKER_UNAVAILABLE"
    status_code = 503

    def __init__(self, cause: Exception | None = None):
        super().__init__(_("Message broker is not reachable"), cause=cause)
