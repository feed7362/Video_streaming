import asyncio
import inspect
import logging
from typing import TYPE_CHECKING, Dict, Optional

from fastapi import status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.health import (
    DatabaseUnavailableError,
    MessageBrokerUnavailableError,
    ObjectStorageUnavailableError,
)
from src.schemas.endpoint import HealthStatus

if TYPE_CHECKING:
    from faststream.rabbit import RabbitBroker

    from src.infrastructure.s3_client import S3Client


class HealthService:
    def __init__(
        self,
        session: AsyncSession,
        s3_client: "S3Client",
        broker: Optional["RabbitBroker"] = None,
    ):
        self.session = session
        self.s3_client = s3_client
        self.broker = broker
        self.checks: Dict[str, str] = {}
        self._statuses: list[int] = []
        self.status_code = status.HTTP_200_OK

    async def _check_database(self):
        try:
            await self.session.execute(text("SELECT 1"))
            self.checks["database"] = "ok"
        except Exception as ex:
            logging.exception("Health: database check failed")
            err = DatabaseUnavailableError(ex)
            self.checks["database"] = err.code
            self._statuses.append(err.status_code)

    async def _check_object_storage(self):
        try:
            await self.s3_client.get_bucket_list()
            self.checks["object_storage"] = "ok"
        except Exception as ex:
            logging.exception("Health: object storage check failed")
            err = ObjectStorageUnavailableError(ex)
            self.checks["object_storage"] = err.code
            self._statuses.append(err.status_code)

    async def _check_message_broker(self):
        if self.broker is None:
            self.checks["message_broker"] = "skipped"
            return

        try:
            is_connected = getattr(self.broker, "is_connected", False)

            if not is_connected:
                connect_result = self.broker.connect()
                if inspect.isawaitable(connect_result):
                    await connect_result

            if not getattr(self.broker, "is_connected", True):
                raise RuntimeError("Message broker not connected")

            self.checks["message_broker"] = "ok"
        except Exception as ex:
            logging.exception("Health: message broker check failed")
            err = MessageBrokerUnavailableError(ex)
            self.checks["message_broker"] = err.code
            self._statuses.append(err.status_code)

    async def check_health(self) -> HealthStatus:
        await asyncio.gather(
            self._check_database(),
            self._check_object_storage(),
            self._check_message_broker(),
        )

        self.status_code = (
            status.HTTP_200_OK if not self._statuses else max(self._statuses)
        )

        return HealthStatus(
            status="ready" if self.status_code == 200 else "not ready",
            details=self.checks,
        )
