import asyncio
import shutil
from pathlib import Path
import subprocess

LOCAL_BASE = Path("/tmp/processing")


# ---------- Utility: safe mkdir / cleanup ----------
def prepare_dirs(video_id: str) -> Path:
    base = LOCAL_BASE / video_id
    out = base / "output"
    for p in (base, out):
        p.mkdir(parents=True, exist_ok=True)
    return base


def cleanup_dirs(video_id: str):
    base = LOCAL_BASE / video_id
    try:
        shutil.rmtree(base)
    except Exception as e:
        print(f"Failed to cleanup local dirs for {video_id}, Error: {e}")


async def stream_ffmpeg(input_async_iter, output_dir: Path):
    out_template = str(output_dir / "output" / "stream_%v" / "seg_%03d.ts")
    out_playlist = str(output_dir / "output" / "stream_%v" / "playlist.m3u8")
    cmd = [
        # input
        "ffmpeg", "-y",
        "-fflags", "+genpts",
        "-hwaccel", "cuda", "-hwaccel_output_format", "cuda",
        "-i", "pipe:0",

        # filter and scaling
        "-filter_complex",
        "[0:v]split=3[v1][v2][v3];"
        "[v1]scale_npp=w=640:h=360:force_original_aspect_ratio=decrease[v360];"
        "[v2]scale_npp=w=1280:h=720:force_original_aspect_ratio=decrease[v720];"
        "[v3]scale_npp=w=1920:h=1080:force_original_aspect_ratio=decrease[v1080]",

        # 360p
        "-map", "[v360]", "-map", "a:0",
        "-c:v:0", "h264_nvenc", "-b:v:0", "800k", "-maxrate:v:0", "800k", "-bufsize:v:0", "1200k",
        "-c:a:0", "aac", "-b:a:0", "96k",

        # 720p
        "-map", "[v720]", "-map", "a:0",
        "-c:v:1", "h264_nvenc", "-b:v:1", "2000k", "-maxrate:v:1", "2000k", "-bufsize:v:1", "3000k",
        "-c:a:1", "aac", "-b:a:1", "128k",

        # 1080p
        "-map", "[v1080]", "-map", "a:0",
        "-c:v:2", "h264_nvenc", "-b:v:2", "5000k", "-maxrate:v:2", "5000k", "-bufsize:v:2", "7500k",
        "-c:a:2", "aac", "-b:a:2", "192k",

        # subtitles
        # "-map", "0:s:0?",
        # "-c:s", "webvtt",

        # preset
        "-rc", "vbr", "-preset", "p1", "-tune:v", "ull",

        # output
        "-f", "hls",
        "-hls_time", "6",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", out_template,
        "-hls_flags", "independent_segments+split_by_time",
        "-master_pl_name", "master.m3u8",
        "-var_stream_map", "v:0,a:0,name:360p v:1,a:1,name:720p v:2,a:2,name:1080p",
        out_playlist
    ]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0
    )

    async def feed_stdin():
        try:
            async for chunk in input_async_iter:
                process.stdin.write(chunk)
                await process.stdin.drain()
        except Exception as e:
            print(f"Error feeding ffmpeg stdin: {e}")
        finally:
            if not process.stdin.is_closing():
                process.stdin.close()
                await process.stdin.wait_closed()

    async def log_stderr():
        while True:
            chunk = await process.stderr.read(1024)
            if not chunk:
                break
            print("[ffmpeg stderr]", chunk.decode(errors='ignore').strip())

    await asyncio.gather(feed_stdin(), log_stderr())

    rc = await process.wait()
    return rc
