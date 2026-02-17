from faststream.rabbit.fastapi import RabbitBroker


async def get_rabbit_broker() -> RabbitBroker:
    """Provide the shared RabbitMQ broker instance for dependency injection."""
    rabbit_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")

    return rabbit_broker
