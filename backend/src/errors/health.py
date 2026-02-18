from src.core.base_error import AppError


class DatabaseUnavailableError(AppError):
    code = "DATABASE_UNAVAILABLE"
    status_code = 503
    message = "Database is unavailable"

    def __init__(self, exception: Exception):
        super().__init__(self.message, cause=exception)


class ObjectStorageUnavailableError(AppError):
    code = "OBJECT_STORAGE_UNAVAILABLE"
    message = "Object storage is not reachable"
    status_code = 503

    def __init__(self, exception: Exception):
        super().__init__(self.message, cause=exception)


class MessageBrokerUnavailableError(AppError):
    code = "MESSAGE_BROKER_UNAVAILABLE"
    message = "Message broker is not reachable"
    status_code = 503

    def __init__(self, exception: Exception):
        super().__init__(self.message, cause=exception)
