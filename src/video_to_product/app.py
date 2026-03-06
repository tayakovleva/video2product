"""FastAPI web application for video-to-product pipeline."""

import os
import shutil
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .download import download_audio
from .summarize import generate_agent_prompt, summarize_transcript
from .transcribe import transcribe_file

app = FastAPI(title="Video to Product")

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# In-memory session storage (single user tool)
session: dict = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "session": session})


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    """Handle uploaded audio/video file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix)
    with open(tmp.name, "wb") as f:
        shutil.copyfileobj(file.file, f)

    session.clear()
    session["source"] = f"file: {file.filename}"
    session["audio_path"] = tmp.name
    session["step"] = "uploaded"
    return RedirectResponse("/", status_code=303)


@app.post("/url")
async def submit_url(request: Request, url: str = Form(...)):
    """Handle YouTube/video URL."""
    session.clear()
    session["source"] = url
    session["step"] = "downloading"

    audio_path = download_audio(url)
    session["audio_path"] = audio_path
    session["step"] = "uploaded"
    return RedirectResponse("/", status_code=303)


@app.post("/transcribe")
async def do_transcribe(request: Request):
    """Run transcription on the uploaded audio."""
    audio_path = session.get("audio_path")
    if not audio_path:
        return RedirectResponse("/", status_code=303)

    session["step"] = "transcribing"
    transcript = transcribe_file(audio_path)
    session["transcript"] = transcript
    session["step"] = "transcribed"

    # Clean up audio
    if os.path.exists(audio_path):
        os.unlink(audio_path)

    return RedirectResponse("/", status_code=303)


@app.post("/summarize")
async def do_summarize(request: Request):
    """Generate summary from transcript."""
    transcript = session.get("transcript")
    if not transcript:
        return RedirectResponse("/", status_code=303)

    summary = summarize_transcript(transcript)
    session["summary"] = summary
    session["step"] = "summarized"
    return RedirectResponse("/", status_code=303)


@app.post("/generate")
async def do_generate(request: Request):
    """Generate agent prompt from summary."""
    summary = session.get("summary")
    if not summary:
        return RedirectResponse("/", status_code=303)

    product = generate_agent_prompt(summary)
    session["product"] = product
    session["step"] = "done"
    return RedirectResponse("/", status_code=303)


@app.post("/reset")
async def reset(request: Request):
    """Clear session and start over."""
    audio_path = session.get("audio_path")
    if audio_path and os.path.exists(audio_path):
        os.unlink(audio_path)
    session.clear()
    return RedirectResponse("/", status_code=303)
