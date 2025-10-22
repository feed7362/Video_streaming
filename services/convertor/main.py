import asyncio
import json
import logging
import math
import shutil
import subprocess
from pathlib import Path
from typing import AsyncIterable

LOCAL_BASE = Path("/tmp/processing")


# ---------- Utility: safe mkdir / cleanup ----------
async def prepare_dirs(video_id: str) -> Path:
    base = LOCAL_BASE / video_id
    base.mkdir(parents=True, exist_ok=True)
    logging.debug(f"Created local dirs for {video_id}")
    return base


def cleanup_dirs(video_id: str) -> None:
    base = LOCAL_BASE / video_id
    try:
        shutil.rmtree(base)
        logging.debug(f"Removed local dirs for {video_id}")
    except Exception as e:
        logging.error(f"Failed to cleanup local dirs for {video_id}, Error: {e}")


def has_gpu():
    try:
        subprocess.run(
            ["nvidia-smi"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        return True
    except Exception:
        return False


async def stream_ffmpeg(
    input_async_iter: AsyncIterable[bytes],
    output_dir: Path,
    fps: int,
    segment_duration: int = 3,
) -> int:
    out_template = str(output_dir / "stream_%v" / "seg_%03d.ts")
    out_playlist = str(output_dir / "stream_%v" / "playlist.m3u8")

    gop_size = math.ceil(fps * segment_duration)
    print(f"Calculated GOP size for -g parameter: {gop_size}")
    use_gpu = has_gpu()

    # ---------- Common base command ----------
    cmd = [
        "ffmpeg",
        "-y",
        "-fflags",
        "+genpts",
    ]

    # ---------- Input & hardware acceleration ----------
    if use_gpu:
        cmd += [
            "-hwaccel",
            "cuda",
            "-hwaccel_output_format",
            "cuda",
        ]
    cmd += ["-i", "pipe:0"]

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
            "[v1]scale=w=640:h=360:force_original_aspect_ratio=decrease[v360];"
            "[v2]scale=w=1280:h=720:force_original_aspect_ratio=decrease[v720];"
            "[v3]scale=w=1920:h=1080:force_original_aspect_ratio=decrease[v1080]"
        )
    cmd += ["-filter_complex", filter_complex]

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
        "a:0",
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
        "a:0",
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
        cmd += ["-rc", "vbr", "-preset", "p1", "-tune:v", "ull"]
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
        "v:0,a:0,name:360p v:1,a:1,name:720p v:2,a:2,name:1080p",
        out_playlist,
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0
    )

    async def feed_stdin() -> None:
        if process.stdin is None:
            logging.error("ffmpeg stdin is None")
            return
        try:
            async for chunk in input_async_iter:
                process.stdin.write(chunk)
                await process.stdin.drain()
        except Exception as e:
            logging.error(f"Error feeding ffmpeg stdin: {e}")
        finally:
            if not process.stdin.is_closing():
                process.stdin.close()
                await process.stdin.wait_closed()

    async def log_stderr() -> None:
        if process.stderr is None:
            logging.error("ffmpeg stderr is None")
            return
        while True:
            chunk = await process.stderr.read(1024)
            if not chunk:
                break
            logging.debug("[ffmpeg stderr] %s", chunk.decode(errors="ignore").strip())

    await asyncio.gather(feed_stdin(), log_stderr())

    rc = await process.wait()
    return rc


async def get_video_properties(
    input_async_iter: AsyncIterable[bytes],
) -> dict[str, float | int]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=r_frame_rate,width,height",
        "-of",
        "json",
        "pipe:0",
    ]

    process = await asyncio.create_subprocess_exec(
        *cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    try:
        if process.stdin is not None:
            async for chunk in input_async_iter:
                if process.stdin.is_closing():
                    break  # ffprobe closed its stdin — stop feeding
                process.stdin.write(chunk)
                await process.stdin.drain()
    except BrokenPipeError:
        logging.warning("ffprobe closed stdin early (likely got enough data).")
    except Exception as e:
        logging.error(f"Error reading initial chunks for ffprobe: {e}")
        process.kill()
        raise
    finally:
        if process.stdin and not process.stdin.is_closing():
            process.stdin.close()

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        logging.error(f"ffprobe stderr: {stderr.decode(errors='ignore')}")
        raise RuntimeError(f"ffprobe failed: {stderr.decode()}")

    data = json.loads(stdout)["streams"][0]
    fps_fraction = data.get("r_frame_rate", "0/1")
    numerator, denominator = map(int, fps_fraction.split("/"))
    fps = numerator / denominator if denominator != 0 else 0

    return {
        "fps": fps,
        "width": data.get("width", 0),
        "height": data.get("height", 0),
    }
