from faststream.rabbit.fastapi import RabbitBroker

shared_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")


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
