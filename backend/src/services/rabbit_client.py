from faststream.rabbit.fastapi import RabbitRouter

rabbit_router = RabbitRouter(url="amqp://guest:guest@localhost:5672/",
                             prefix="/api/rabbit",)
