# Microservices

Workers and helper services that sit alongside the BFF. Communicate exclusively via RabbitMQ (one queue per concern).

## `convertor/` — video transcoder

- **Runtime**: Python 3.12 + FastStream (RabbitMQ) + FastAPI (for health/metrics) on top of the `jrottenberg/ffmpeg:7.1-nvidia2204` base image. Requires an NVIDIA GPU + the Container Toolkit for NVENC.
- **Inputs**: messages on the `video.encode` queue containing the S3 object name.
- **Pipeline**:
  1. Generates a presigned URL for the source video.
  2. Probes FPS / audio with ffprobe; raises `InvalidMediaError` if metadata is missing.
  3. Transcodes to HLS in three rungs (360p / 720p / 1080p) using NVENC; on `FFmpegExecutionError` it falls back to CPU (`-c:v libx264`) for that attempt.
  4. Uploads the HLS tree (`master.m3u8` + per-rendition playlists + .ts segments) back to MinIO.
  5. Publishes `video.encode.status` events at each stage (`processing` → `ready` / `retrying` / `failed`).

### Retry topology

```
video.encode  (work queue, DLX = video.dlx)
  │
  │  app-level retry (x-retry-count header, max = 3)
  ▼
video.encode  (re-publish with attempt+1)
  │
  │  after 3 failed attempts
  ▼
video.failed       (terminal event for external observers)
video.encode.status (status=failed, so the BFF status handler marks the DB row Failed)

video.dlx    (DLX fanout) ─► video.encode.dlq  (broker-level safety net for nacked / unroutable messages)
```

`MAX_RETRIES = 3` in `main.py`. The convertor publishes via `correlation_id=` + `headers={"x-request-id": rid}` so the original BFF request's `[rid=…]` flows into every log line and downstream event.

### Health + metrics

- `/api/health/live` — liveness only (no dependency checks here; that's the BFF's job).
- `/api/metrics` — Prometheus counters and histograms for encode duration, failures, GPU fallback rate.

## `moderation/` — content moderation (stub)

Placeholder for NSFW / policy scanning. Reads from a moderation queue when implemented; would publish `moderation.result` events back. Currently a `print("hello")` stub — useful as the second consumer when iterating on RabbitMQ topology.

If you want this real, minimal scope:
- Frame-sample → CLIP / OpenNSFW2 classification.
- Threshold-based block → publish `video.moderated` with verdict.
- Wire to the BFF as another `video.events` subscriber that updates `Video.privacy` or sets a moderation status.

## Why not in the BFF?

- Encoding is CPU- and GPU-heavy; isolating it from request-serving keeps the API responsive.
- Async fan-out via RabbitMQ trivially supports horizontal scaling (run N convertor replicas; queue distributes work).
- Failures in encode shouldn't crash the API — DLQ + retry budget enforce that boundary.
