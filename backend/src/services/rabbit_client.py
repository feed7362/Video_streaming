from faststream.rabbit import RabbitBroker

rabbit_broker = RabbitBroker(url="amqp://guest:guest@localhost:5672/")

@rabbit_broker.subscriber("video.encode.status")
async def status_handler(video_id: str, status: str):
    print(f"Video {video_id} is {status}")