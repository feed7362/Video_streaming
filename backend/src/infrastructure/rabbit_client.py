from faststream.rabbit.fastapi import RabbitBroker

rabbit_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")


async def get_rabbit_broker() -> RabbitBroker:
    """Provide the shared RabbitMQ broker instance for dependency injection."""

    return rabbit_broker
