import uuid
from faststream.rabbit import RabbitBroker
from faststream import FastStream
import aiofiles
from main import stream_ffmpeg, prepare_dirs, cleanup_dirs

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
app = FastStream(broker)


@broker.subscriber("video.encode")
async def encode_video(video_id: str):
    id = uuid.uuid4().hex
    base_dir = prepare_dirs(id)

    async def file_reader_async(path: str, chunk_size: int = 30 * 1024 * 1024):
        async with aiofiles.open(path, "rb") as f:
            while True:
                chunk = await f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    try:
        async_gen = file_reader_async(video_path)
        await stream_ffmpeg(async_gen, base_dir)
        await broker.publish({"video_id": video_id, "status": "pending"}, queue="video.encode.status")
    finally:
        await broker.publish({"video_id": video_id, "status": "done"}, queue="video.encode.status")
        # cleanup_dirs(video_id)


# @app.after_startup
# async def send_test_message():
#     await broker.publish("./videoplayback.mp4", queue="video.encode")
