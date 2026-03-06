"""Audio transcription via OpenAI Whisper API with chunking for large files."""

import os
import tempfile
from pathlib import Path

from openai import OpenAI
from pydub import AudioSegment

MAX_CHUNK_SIZE_MB = 24
MAX_CHUNK_SIZE_BYTES = MAX_CHUNK_SIZE_MB * 1024 * 1024
CHUNK_DURATION_MS = 10 * 60 * 1000  # 10 minutes


def split_audio(file_path: str) -> list[str]:
    """Split audio file into chunks if it exceeds Whisper API limit (25 MB)."""
    if os.path.getsize(file_path) <= MAX_CHUNK_SIZE_BYTES:
        return [file_path]

    audio = AudioSegment.from_file(file_path)
    chunks = []
    tmp_dir = tempfile.mkdtemp(prefix="v2p_chunks_")

    for i, start in enumerate(range(0, len(audio), CHUNK_DURATION_MS)):
        chunk = audio[start : start + CHUNK_DURATION_MS]
        chunk_path = os.path.join(tmp_dir, f"chunk_{i:03d}.mp3")
        chunk.export(chunk_path, format="mp3", bitrate="128k")
        chunks.append(chunk_path)

    return chunks


def transcribe_file(file_path: str) -> str:
    """Transcribe an audio file, splitting into chunks if needed."""
    client = OpenAI()
    chunks = split_audio(file_path)
    parts = []

    for chunk_path in chunks:
        with open(chunk_path, "rb") as f:
            result = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language="ru",
            )
        parts.append(result.text)

        # Clean up chunk if it's a temp file
        if chunk_path != file_path:
            os.unlink(chunk_path)

    # Clean up temp dir
    if chunks and chunks[0] != file_path:
        os.rmdir(Path(chunks[0]).parent)

    return "\n\n".join(parts)
