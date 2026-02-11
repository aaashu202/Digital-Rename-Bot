import os
import asyncio
import json
from helper.utils import metadata_text


# ===== DEFAULT METADATA (from environment variables) =====
DEFAULT_AUTHOR = os.getenv("DEFAULT_AUTHOR", "Vist our Telegram channel @Dramafilez")
DEFAULT_TITLE = os.getenv("DEFAULT_TITLE", "Vist our Telegram channel @Dramafilez")
DEFAULT_VIDEO_TITLE = os.getenv("DEFAULT_VIDEO_TITLE", "Vist our Telegram channel @Dramafilez")
DEFAULT_AUDIO_TITLE = os.getenv("DEFAULT_AUDIO_TITLE", "@Dramafilez")
DEFAULT_SUBTITLE_TITLE = os.getenv("DEFAULT_SUBTITLE_TITLE", "@Dramafilez")


async def change_metadata(input_file, output_file, metadata):
    # Get metadata from your helper
    author, title, video_title, audio_title, subtitle_title = await metadata_text(metadata)

    # Apply defaults if user didn't provide values
    author = author or DEFAULT_AUTHOR
    title = title or DEFAULT_TITLE
    video_title = video_title or DEFAULT_VIDEO_TITLE
    audio_title = audio_title or DEFAULT_AUDIO_TITLE
    subtitle_title = subtitle_title or DEFAULT_SUBTITLE_TITLE

    # -------- Run ffprobe --------
    probe = await asyncio.create_subprocess_exec(
        "ffprobe",
        "-v", "error",
        "-show_streams",
        "-print_format", "json",
        input_file,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await probe.communicate()

    if probe.returncode != 0:
        print("FFprobe error:", stderr.decode())
        return False

    data = json.loads(stdout.decode())
    streams = data.get("streams", [])

    # -------- Build ffmpeg command --------
    cmd = [
        "ffmpeg",
        "-y",  # overwrite output
        "-i", input_file,
        "-map", "0",
        "-c", "copy",  # copy all streams (no re-encode)
        "-metadata", f"title={title}",
        "-metadata", f"author={author}",
        "-metadata", "comment=Added by @Digital_Rename_Bot",
    ]

    video_index = 0
    audio_index = 0
    subtitle_index = 0

    for stream in streams:
        codec_type = stream.get("codec_type")

        if codec_type == "video":
            cmd.extend([
                f"-metadata:s:v:{video_index}",
                f"title={video_title}"
            ])
            video_index += 1

        elif codec_type == "audio":
            cmd.extend([
                f"-metadata:s:a:{audio_index}",
                f"title={audio_title}"
            ])
            audio_index += 1

        elif codec_type == "subtitle":
            cmd.extend([
                f"-metadata:s:s:{subtitle_index}",
                f"title={subtitle_title}"
            ])
            subtitle_index += 1

    cmd.extend(["-f", "matroska", output_file])

    print("Running:", " ".join(cmd))

    # -------- Run ffmpeg --------
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print("FFmpeg error:", stderr.decode())
        return False

    return True
