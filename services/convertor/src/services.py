import asyncio
import json
import logging
import math
import shutil
import subprocess
from pathlib import Path

from .exceptions import (
    DirectoryPrepareError,
    FFmpegExecutionError,
    FFmpegStartError,
    FFProbeError,
    InvalidMediaError,
)
from .schemas import VideoProperties

LOCAL_BASE = Path("/tmp/processing")


# ---------- Utility: safe mkdir / cleanup ----------
async def prepare_dirs(video_id: str) -> Path:
    base = LOCAL_BASE / video_id
    try:
        base.mkdir(parents=True, exist_ok=True)
        logging.debug(f"Created local dirs for {video_id}")
        return base
    except Exception as e:
        raise DirectoryPrepareError(video_id) from e


def cleanup_dirs(video_id: str) -> None:
    base = LOCAL_BASE / video_id
    if not base.exists():
        logging.warning(f"Cleanup skipped — {base} does not exist")
        return
    try:
        shutil.rmtree(base)
        logging.debug(f"Removed local dirs for {video_id}")
    except Exception as e:
        logging.error(f"Failed to cleanup local dirs for {video_id}, Error: {e}")
        raise DirectoryPrepareError(video_id) from e


def has_gpu() -> bool:
    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        test_cmd = [
            "ffmpeg",
            "-hide_banner",
            "-v",
            "error",
            "-f",
            "lavfi",
            "-i",
            "color=black:s=64x64:d=1",
            "-c:v",
            "h264_nvenc",
            "-f",
            "null",
            "-",
        ]
        subprocess.run(
            test_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        logging.warning(
            "NVENC initialization failed or GPU missing. Falling back to CPU encoding."
        )
        return False


async def stream_ffmpeg(
    url: str,
    output_dir: Path,
    fps: int,
    segment_duration: int = 3,
    has_audio: bool = True,
    force_cpu: bool = False,
) -> int:
    out_template = str(output_dir / "stream_%v" / "seg_%03d.ts")
    out_playlist = str(output_dir / "stream_%v" / "playlist.m3u8")

    gop_size = math.ceil(fps * segment_duration)
    logging.info(f"Calculated GOP size for -g parameter: {gop_size}")
    use_gpu = has_gpu() and not force_cpu

    # ---------- Common base command ----------
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-analyzeduration",
        "100M",
        "-probesize",
        "100M",
        "-y",
    ]

    # ---------- Input & hardware acceleration ----------
    if use_gpu:
        cmd += [
            "-hwaccel",
            "cuda",
            "-hwaccel_output_format",
            "cuda",
        ]
    cmd += ["-i", url]

    # ---------- Filter & scaling ----------
    if use_gpu:
        filter_complex = (
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale_npp=w=640:h=360:force_original_aspect_ratio=decrease[v360];"
            "[v2]scale_npp=w=1280:h=720:force_original_aspect_ratio=decrease[v720];"
            "[v3]scale_npp=w=1920:h=1080:force_original_aspect_ratio=decrease[v1080]"
        )
    else:
        filter_complex = (
            "[0:v]split=3[v1][v2][v3];"
            "[v1]scale=w=640:h=360:force_original_aspect_ratio=decrease,"
            "pad=ceil(iw/2)*2:ceil(ih/2)*2[v360];"
            "[v2]scale=w=1280:h=720:force_original_aspect_ratio=decrease,"
            "pad=ceil(iw/2)*2:ceil(ih/2)*2[v720];"
            "[v3]scale=w=1920:h=1080:force_original_aspect_ratio=decrease,"
            "pad=ceil(iw/2)*2:ceil(ih/2)*2[v1080]"
        )
    cmd += ["-filter_complex", filter_complex]
    if has_audio:
        var_stream_map = "v:0,a:0,name:360p v:1,a:1,name:720p v:2,a:2,name:1080p"
    else:
        var_stream_map = "v:0,name:360p v:1,name:720p v:2,name:1080p"
    # ---------- Codec setup ----------
    vcodec = "h264_nvenc" if use_gpu else "libx264"

    cmd += [
        # 360p
        "-map",
        "[v360]",
        "-map",
        "a:0?",
        "-c:v:0",
        vcodec,
        "-b:v:0",
        "800k",
        "-maxrate:v:0",
        "800k",
        "-bufsize:v:0",
        "1200k",
        "-c:a:0",
        "aac",
        "-b:a:0",
        "96k",
        # 720p
        "-map",
        "[v720]",
        "-map",
        "a:0?",
        "-c:v:1",
        vcodec,
        "-b:v:1",
        "2000k",
        "-maxrate:v:1",
        "2000k",
        "-bufsize:v:1",
        "3000k",
        "-c:a:1",
        "aac",
        "-b:a:1",
        "128k",
        # 1080p
        "-map",
        "[v1080]",
        "-map",
        "a:0?",
        "-c:v:2",
        vcodec,
        "-b:v:2",
        "5000k",
        "-maxrate:v:2",
        "5000k",
        "-bufsize:v:2",
        "7500k",
        "-c:a:2",
        "aac",
        "-b:a:2",
        "192k",
    ]

    # ---------- Preset / Rate control ----------
    if use_gpu:
        cmd += [
            "-rc:v:0",
            "vbr",
            "-rc:v:1",
            "vbr",
            "-rc:v:2",
            "vbr",
            "-preset:v:0",
            "p4",
            "-preset:v:1",
            "p4",
            "-preset:v:2",
            "p4",
        ]
    else:
        cmd += ["-preset", "veryfast", "-tune", "zerolatency"]

    # ---------- Output ----------
    cmd += [
        "-f",
        "hls",
        "-g",
        str(gop_size),
        "-keyint_min",
        str(gop_size),
        "-sc_threshold",
        "0",
        "-hls_time",
        str(segment_duration),
        "-hls_playlist_type",
        "vod",
        "-hls_segment_filename",
        out_template,
        "-hls_flags",
        "independent_segments+split_by_time",
        "-master_pl_name",
        "master.m3u8",
        "-var_stream_map",
        var_stream_map,
        out_playlist,
    ]
    try:
        process = await asyncio.create_subprocess_exec(*cmd, stderr=subprocess.PIPE)
    except Exception as e:
        raise FFmpegStartError() from e

    stderr_output = []

    async def log_stderr() -> None:
        if process.stderr is None:
            return
        while True:
            chunk = await process.stderr.read(1024)
            if not chunk:
                break
            decoded = chunk.decode(errors="ignore").strip()
            stderr_output.append(decoded)
            logging.debug("[ffmpeg stderr] %s", decoded)

    await log_stderr()
    rc = await process.wait()
    if rc != 0:
        tail = "\n".join(stderr_output[-5:]) if stderr_output else "No stderr output"
        raise FFmpegExecutionError(return_code=rc, stderr=tail)
    return rc


async def get_video_properties(url: str) -> VideoProperties:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_streams",
        "-of",
        "json",
        url,
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as e:
        raise FFProbeError(details="Failed to start ffprobe process") from e

    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        logging.error(f"ffprobe stderr: {stderr.decode(errors='ignore')}")
        raise FFProbeError(details=stderr.decode(errors="ignore"))

    try:
        info = json.loads(stdout)
    except json.JSONDecodeError as e:
        raise FFProbeError(details="Failed to parse ffprobe JSON output") from e

    streams = info.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    has_audio = any(s.get("codec_type") == "audio" for s in streams)

    if not video_stream:
        raise InvalidMediaError("No video stream found in the file")

    fps_fraction = video_stream.get("r_frame_rate", "0/1")
    num, den = map(int, fps_fraction.split("/"))
    fps = num / den if den else 0

    # Cast bit_rate safely
    bit_rate = video_stream.get("bit_rate", 0)
    try:
        bit_rate = int(bit_rate)
    except (ValueError, TypeError):
        bit_rate = 0

    return VideoProperties(
        fps=fps,
        width=video_stream.get("width", 0),
        height=video_stream.get("height", 0),
        bitrate=bit_rate // 1000 if bit_rate else 0,
        has_audio=has_audio,
    )


async def check_liveness(scope, receive, send):
    if scope["type"] == "http":
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [(b"content-type", b"application/json")],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps({"status": "ok"}).encode("utf-8"),
            }
        )
