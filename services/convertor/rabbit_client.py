from faststream.rabbit import RabbitBroker
from faststream import FastStream
from main import stream_ffmpeg, prepare_dirs, cleanup_dirs
from s3_client import s3_client

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
app = FastStream(broker)


@broker.subscriber("video.encode")
async def encode_video(video_id: str):
    try:
        base_dir = await prepare_dirs(video_id)
        async_gen = s3_client.download_file(video_id, 1024 * 1024 * 30)

        await broker.publish({"video_id": video_id, "status": "pending"}, queue="video.encode.status")
        await stream_ffmpeg(async_gen, base_dir)

        await s3_client.upload_dir(video_id, base_dir)
        await broker.publish({"video_id": video_id, "status": "done"}, queue="video.encode.status")

    except Exception as e:
        await broker.publish({"video_id": video_id, "status": f"error: {e}"}, queue="video.encode.status")
    finally:
        cleanup_dirs(video_id)
        await s3_client.delete_file(video_id)
