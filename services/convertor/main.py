import logging
import os
from pathlib import Path

from faststream import Context
from faststream.asgi import AsgiFastStream
from faststream.rabbit import (
    ExchangeType,
    RabbitBroker,
    RabbitExchange,
    RabbitMessage,
    RabbitQueue,
)
from prometheus_client import CollectorRegistry, make_asgi_app

from src.config import get_rabbitmq_settings
from src.correlation import get_request_id, install_log_filter, set_request_id
from src.exceptions import AppError, FFmpegExecutionError, InvalidMediaError
from src.s3_client import get_s3_client
from src.services import (
    check_liveness,
    cleanup_dirs,
    get_video_properties,
    prepare_dirs,
    stream_ffmpeg,
)

install_log_filter()

MAX_RETRIES = 3  # after this many attempts the job goes to video.failed and is dropped

settings = get_rabbitmq_settings()
broker = RabbitBroker(settings.rabbitmq_url)
registry = CollectorRegistry()
app = AsgiFastStream(
    broker,
    asgi_routes=[
        ("/api/metrics", make_asgi_app(registry)),
        ("/api/health/live", check_liveness),
    ],
)

# ── Topology ────────────────────────────────────────────────────────────────
# video.encode  -- main work queue. Dead-letters to video.dlx on nack.
# video.dlx     -- DLX fanout; routes failed messages into video.encode.dlq.
# video.encode.dlq -- holds messages that exhausted retries; ops can inspect/replay.
# video.failed  -- terminal status published to consumers (e.g. BFF) when a video
#                  has been given up on, so the DB row can be marked Failed.
encode_dlx = RabbitExchange("video.dlx", type=ExchangeType.FANOUT, durable=True)
encode_dlq = RabbitQueue(
    "video.encode.dlq",
    durable=True,
)
encode_queue = RabbitQueue(
    "video.encode",
    durable=True,
    arguments={
        "x-dead-letter-exchange": "video.dlx",
    },
)


@broker.subscriber(encode_queue)
async def encode_video(
    filename: str,
    msg: RabbitMessage = Context(),
) -> None:
    # Pull rid from header (preferred) or message correlation_id.
    headers = dict(msg.headers or {})
    rid = headers.get("x-request-id") or getattr(msg, "correlation_id", None) or "-"
    set_request_id(str(rid))

    # Retry accounting — message header survives nack/requeue.
    # `x-death` is RabbitMQ's built-in counter (set when DLX cycles a message
    # back to the original queue), but we maintain our own header for clarity.
    attempt = int(headers.get("x-retry-count", 0)) + 1
    s3_client = get_s3_client()
    video_id = Path(filename).stem

    if attempt > MAX_RETRIES:
        logging.error(
            "Giving up on video after %d attempts; publishing video.failed",
            MAX_RETRIES,
            extra={"video_id": video_id},
        )
        # 1) Terminal event for external observers (DLQ-style consumers).
        await broker.publish(
            {
                "video_id": video_id,
                "status": "failed",
                "reason": "max_retries_exceeded",
                "attempts": attempt - 1,
            },
            exchange="video.events",
            routing_key="video.failed",
            correlation_id=get_request_id(),
            headers={"x-request-id": get_request_id()},
        )
        # 2) Status update on the existing channel so the BFF's status_handler
        #    marks the DB row Failed (no duplicated persistence logic).
        await broker.publish(
            {"video_id": video_id, "status": "failed"},
            exchange="video.events",
            routing_key="video.encode.status",
            correlation_id=get_request_id(),
            headers={"x-request-id": get_request_id()},
        )
        # Cleanup any partial state and ACK so RabbitMQ drops the message.
        cleanup_dirs(video_id)
        try:
            await s3_client.delete_file(filename, bucket_name="videos")
        except Exception:  # noqa: BLE001 - best-effort cleanup
            logging.exception("Failed to delete dead-letter source from S3")
        return

    try:
        base_dir = await prepare_dirs(video_id)

        await broker.publish(
            {"video_id": video_id, "status": "processing"},
            exchange="video.events",
            routing_key="video.encode.status",
            correlation_id=get_request_id(),
            headers={"x-request-id": get_request_id()},
        )

        video_url = await s3_client.generate_presigned_url(
            filename, bucket_name="videos", expiry=7200
        )
        properties = await get_video_properties(video_url)
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

        try:
            await stream_ffmpeg(
                video_url,
                base_dir,
                int(round(properties.fps)),
                3,
                properties.has_audio,
            )
        except FFmpegExecutionError:
            logging.warning(
                "GPU encoding failed, retrying with CPU...",
                extra={"video_id": video_id},
            )
            cleanup_dirs(video_id)
            base_dir = await prepare_dirs(video_id)
            await stream_ffmpeg(
                video_url,
                base_dir,
                int(round(properties.fps)),
                3,
                properties.has_audio,
                force_cpu=True,
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
            exchange="video.events",
            routing_key="video.encode.status",
            correlation_id=get_request_id(),
            headers={"x-request-id": get_request_id()},
        )

        logging.info("Video encoding completed", extra={"video_id": video_id})

        await s3_client.delete_file(filename, bucket_name="videos")

    except AppError as exc:
        logging.exception(
            "Encoding error (attempt %d/%d): %s",
            attempt,
            MAX_RETRIES,
            exc,
            extra={"video_id": video_id},
        )
        await broker.publish(
            {
                "video_id": video_id,
                "status": "retrying" if attempt < MAX_RETRIES else "failed",
                "attempt": attempt,
            },
            exchange="video.events",
            routing_key="video.encode.status",
            correlation_id=get_request_id(),
            headers={"x-request-id": get_request_id()},
        )
        # Republish to ourselves with incremented retry counter. We *don't* nack
        # to the DLX here because we want app-level control: AMQPs DLX cycles
        # would lose our headers' attempt count semantics. The terminal handler
        # at the top of this function takes the message to video.failed.
        if attempt < MAX_RETRIES:
            await broker.publish(
                filename,
                queue="video.encode",
                priority=10,
                correlation_id=get_request_id(),
                headers={
                    "x-request-id": get_request_id(),
                    "x-retry-count": str(attempt),
                },
            )
        else:
            await broker.publish(
                {
                    "video_id": video_id,
                    "status": "failed",
                    "reason": str(exc),
                    "attempts": attempt,
                },
                exchange="video.events",
                routing_key="video.failed",
                correlation_id=get_request_id(),
                headers={"x-request-id": get_request_id()},
            )

    finally:
        cleanup_dirs(video_id)
        logging.debug("Cleanup completed", extra={"video_id": video_id})


# DLQ consumer — exists primarily to (a) force declaration of the DLQ + binding
# to video.dlx on startup, and (b) give us a place to observe broker-level
# rejections (e.g. messages nacked without requeue, channel errors). The
# app-level retry path above goes through video.failed, not the DLQ.
@broker.subscriber(encode_dlq, encode_dlx)
async def on_dead_letter(
    body: str,
    msg: RabbitMessage = Context(),
) -> None:
    headers = dict(msg.headers or {})
    logging.error(
        "DLQ received message: body=%s headers=%s",
        body[:200] if isinstance(body, str) else body,
        headers,
    )
