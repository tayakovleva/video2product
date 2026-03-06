"""Download audio from YouTube via yt-dlp."""

import tempfile

import yt_dlp


def download_audio(url: str) -> str:
    """Download audio from a YouTube URL, return path to the file."""
    tmp_dir = tempfile.mkdtemp(prefix="v2p_dl_")
    output_path = f"{tmp_dir}/audio.%(ext)s"

    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "128",
            }
        ],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    return f"{tmp_dir}/audio.mp3"
