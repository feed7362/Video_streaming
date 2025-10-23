import logging

from faststream.rabbit import RabbitBroker

from ..schemas.endpoint import StatusMessage

rabbit_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")


def get_rabbit_broker() -> RabbitBroker:
    """Provide the shared RabbitMQ broker instance for dependency injection."""

    return rabbit_broker


@rabbit_broker.subscriber("video.encode.status")
async def status_handler(msg: StatusMessage) -> None:
    logging.info(f"Video {msg.video_id} is {msg.status}")
