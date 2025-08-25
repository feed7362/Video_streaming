from faststream.rabbit import RabbitBroker

from ..schemas.endpoint import StatusMessage
import logging

rabbit_broker = RabbitBroker(url="amqp://guest:guest@rabbitmq:5672/")


@rabbit_broker.subscriber("video.encode.status")
async def status_handler(msg: StatusMessage):
    logging.info(f"Video {msg.video_id} is {msg.status}")
