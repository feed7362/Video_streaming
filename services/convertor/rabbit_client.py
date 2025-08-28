import logging

from faststream.asgi import AsgiFastStream
from faststream.rabbit import RabbitBroker
from prometheus_client import CollectorRegistry, make_asgi_app

from main import cleanup_dirs, prepare_dirs, stream_ffmpeg
from s3_client import s3_client

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
registry = CollectorRegistry()
app = AsgiFastStream(
    broker,
    asgi_routes=[
        ("/api/metrics", make_asgi_app(registry)),
    ],
)


@broker.subscriber("video.encode")
async def encode_video(video_id: str) -> None:
    try:
        base_dir = await prepare_dirs(video_id)
        async_gen = s3_client.download_file(video_id, 1024 * 1024 * 30)
        logging.debug("[ffmpeg] Starting encoding task for video %s", video_id)

        await broker.publish(
            {"video_id": video_id, "status": "pending"}, queue="video.encode.status"
        )
        await stream_ffmpeg(async_gen, base_dir)
        logging.debug(f"Encoding task for video: {video_id} finished")

        await s3_client.upload_dir(video_id, base_dir)
        await broker.publish(
            {"video_id": video_id, "status": "done"}, queue="video.encode.status"
        )
        logging.info("[S3] Video %s fully uploaded to S3", video_id)

    except Exception as e:
        await broker.publish(
            {"video_id": video_id, "status": f"error: {e}"}, queue="video.encode.status"
        )
        logging.error("[Error] Encoding video %s failed: %s", video_id, e)
    finally:
        cleanup_dirs(video_id)
        await s3_client.delete_file(video_id)
        logging.debug("[Cleanup] Local dirs for video %s removed", video_id)
