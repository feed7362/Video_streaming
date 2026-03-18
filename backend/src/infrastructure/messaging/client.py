from faststream.rabbit.fastapi import RabbitBroker

from src.config import get_rabbitmq_settings

settings = get_rabbitmq_settings()
shared_broker = RabbitBroker(url=settings.rabbitmq_url)


async def get_rabbit_broker() -> RabbitBroker:
    """
    Asynchronous function to retrieve a shared RabbitMQ broker instance.

    This function provides access to a globally shared instance of a RabbitMQ broker,
    allowing for message publishing and consuming functionalities in a distributed
    application. The broker ensures efficient communication between different
    components of the system.

    Returns:
        RabbitBroker: The shared RabbitMQ broker instance.
    """
    return shared_broker
