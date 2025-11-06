import logging
import os
from pathlib import Path

from faststream.asgi import AsgiFastStream
from faststream.rabbit import RabbitBroker
from prometheus_client import CollectorRegistry, make_asgi_app

from main import cleanup_dirs, get_video_properties, prepare_dirs, stream_ffmpeg
from s3_client import get_s3_client

broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
registry = CollectorRegistry()
app = AsgiFastStream(
    broker,
    asgi_routes=[
        ("/api/metrics", make_asgi_app(registry)),
    ],
)


@broker.subscriber("video.encode")
async def encode_video(filename: str) -> None:
    """
    Receives a filename (could include '.mp4'), downloads from S3,
    encodes to HLS, uploads segments, and publishes a status message.
    """
    s3_client = get_s3_client()
    video_id = Path(filename).stem
    base_dir = await prepare_dirs(filename)
    try:
        await broker.publish(
            {"video_id": video_id, "status": "processing"}, queue="video.encode.status"
        )

        probe_stream = s3_client.download_file_by_range(
            object_name=filename,
            range_start=0,
            range_end=5 * 1024 * 1024,
            bucket_name="videos",  # 0 - 5MB
        )
        properties = await get_video_properties(probe_stream)
        fps = properties.get("fps")
        has_audio = bool(properties.get("has_audio"))
        if not fps:
            await broker.publish(
                {"video_id": video_id, "status": "failed"},
                queue="video.encode.status",
            )
            raise ValueError("Could not determine FPS from video metadata.")
        logging.info(f"Detected FPS: {fps:.2f}.")

        async_gen = s3_client.download_file(
            filename, 1024 * 1024 * 30, bucket_name="videos"
        )
        logging.debug("[ffmpeg] Starting encoding task for video %s", video_id)

        await stream_ffmpeg(async_gen, base_dir, int(round(fps)), 3, has_audio)
        logging.debug(f"Encoding task for video: {video_id} finished")

        await s3_client.upload_dir(video_id, base_dir, bucket_name="videos")
        resolutions = []
        for subdir in os.listdir(base_dir):
            if subdir.startswith("stream_"):
                height = int(subdir.replace("stream_", "").replace("p", ""))
                playlist_path = f"{video_id}/{subdir}/playlist.m3u8"
                resolutions.append(
                    {
                        "height": height,
                        "width": (
                            1920 if height == 1080 else 1280 if height == 720 else 854
                        ),
                        "bitrate": (
                            4500 if height == 1080 else 2500 if height == 720 else 1200
                        ),
                        "playlist_path": playlist_path,
                    }
                )
        await broker.publish(
            {
                "video_id": video_id,
                "status": "ready",
                "resolutions": resolutions,
                "video_path": f"{video_id}/master.m3u8",
            },
            queue="video.encode.status",
        )
        logging.info("[S3] Video %s fully uploaded to S3", filename)

    except Exception as e:
        await broker.publish(
            {"video_id": video_id, "status": "failed"}, queue="video.encode.status"
        )
        logging.error("[Error] Encoding video %s failed: %s", filename, e)
    finally:
        cleanup_dirs(video_id)
        await s3_client.delete_file(filename, bucket_name="videos")
        logging.debug("[Cleanup] Local dirs for video %s removed", filename)
