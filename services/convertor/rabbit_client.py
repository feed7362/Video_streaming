from faststream.rabbit import RabbitBroker
from faststream.asgi import AsgiFastStream
from main import stream_ffmpeg, prepare_dirs, cleanup_dirs
from s3_client import s3_client
from prometheus_client import CollectorRegistry, make_asgi_app
import logging

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
registry = CollectorRegistry()
app = AsgiFastStream(
    broker,
    asgi_routes=[
        ("/api/metrics", make_asgi_app(registry)),
    ]
)


@broker.subscriber("video.encode")
async def encode_video(video_id: str):
    try:
        base_dir = await prepare_dirs(video_id)
        async_gen = s3_client.download_file(video_id, 1024 * 1024 * 30)
        logging.info(f"Starting encoding task for video: {video_id}")

        await broker.publish({"video_id": video_id, "status": "pending"}, queue="video.encode.status")
        await stream_ffmpeg(async_gen, base_dir)
        logging.info(f"Encoding task for video: {video_id} finished")

        await s3_client.upload_dir(video_id, base_dir)
        await broker.publish({"video_id": video_id, "status": "done"}, queue="video.encode.status")
        logging.info(f"Video: {video_id} uploaded to S3")

    except Exception as e:
        await broker.publish({"video_id": video_id, "status": f"error: {e}"}, queue="video.encode.status")
        logging.error(f"Error encoding video: {e}")
    finally:
        cleanup_dirs(video_id)
        await s3_client.delete_file(video_id)
        logging.info(f"Cleaned up local dirs for video: {video_id}")
