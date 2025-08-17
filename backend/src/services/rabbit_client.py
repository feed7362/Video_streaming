from faststream.rabbit import RabbitBroker

from ..schemas.endpoint_schema import StatusMessage

rabbit_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")


@rabbit_broker.subscriber("video.encode.status")
async def status_handler(msg: StatusMessage):
    print(f"Video {msg.video_id} is {msg.status}")
