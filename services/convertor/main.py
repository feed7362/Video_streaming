import logging
import os
from pathlib import Path

from faststream.asgi import AsgiFastStream
from faststream.rabbit import RabbitBroker
from prometheus_client import CollectorRegistry, make_asgi_app

from src.exceptions import AppError, InvalidMediaError
from src.s3_client import get_s3_client
from src.services import cleanup_dirs, get_video_properties, prepare_dirs, stream_ffmpeg

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
    s3_client = get_s3_client()
    video_id = Path(filename).stem

    try:
        # 1. Now safely inside the try block.
        # (Assuming services.py already raises DirectoryPrepareError on failure)
        base_dir = await prepare_dirs(video_id)

        await broker.publish(
            {"video_id": video_id, "status": "processing"},
            queue="video.encode.status",
        )

        probe_stream = s3_client.download_file_by_range(
            object_name=filename,
            range_start=0,
            range_end=5 * 1024 * 1024,
            bucket_name="videos",
        )

        properties = await get_video_properties(probe_stream)
        if not properties.fps:
            raise InvalidMediaError("could not determine FPS from video metadata")

        logging.info(
            "Detected video properties",
            extra={
                "video_id": video_id,
                "fps": properties.fps,
                "has_audio": properties.has_audio,
            },
        )

        async_gen = s3_client.download_file(
            filename,
            1024 * 1024 * 30,
            bucket_name="videos",
        )

        await stream_ffmpeg(
            async_gen,
            base_dir,
            int(round(properties.fps)),
            3,
            properties.has_audio,
        )

        await s3_client.upload_dir(video_id, base_dir, bucket_name="videos")

        resolutions = []
        for subdir in os.listdir(base_dir):
            if subdir.startswith("stream_"):
                height = int(subdir.replace("stream_", "").replace("p", ""))
                resolutions.append(
                    {
                        "height": height,
                        "width": (
                            1920 if height == 1080 else 1280 if height == 720 else 854
                        ),
                        "bitrate": (
                            4500 if height == 1080 else 2500 if height == 720 else 1200
                        ),
                        "playlist_path": f"{video_id}/{subdir}/playlist.m3u8",
                    }
                )

        await broker.publish(
            {
                "video_id": video_id,
                "status": "ready",
                "resolutions": resolutions,
                "video_path": f"minio/videos/{video_id}/master.m3u8",
            },
            queue="video.encode.status",
        )

        logging.info("Video encoding completed", extra={"video_id": video_id})

        # 2. Moved deletion here so it ONLY happens if everything above succeeds.
        await s3_client.delete_file(filename, bucket_name="videos")

    except AppError:
        await broker.publish(
            {"video_id": video_id, "status": "failed"},
            queue="video.encode.status",
        )

        logging.exception(
            "Unhandled encoding error",
            extra={"video_id": video_id},
        )

    finally:
        cleanup_dirs(video_id)
        logging.debug("Cleanup completed", extra={"video_id": video_id})
