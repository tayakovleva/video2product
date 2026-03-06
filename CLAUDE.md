# video-to-product — instructions for Claude Code

## Working directory
`/home/tatiana/video-to-product`

## What is this
Персональный веб-инструмент: видео (YouTube / файл) -> транскрипт -> саммари -> продукт (промпт для агента).

## Tech stack
Python 3.12, uv, FastAPI, Jinja2, yt-dlp, OpenAI Whisper API, Anthropic SDK

## Commands
```bash
uv run ruff check src/      # lint
uv run ruff format src/     # format
uv run uvicorn src.app:app --reload --port 8002  # local dev
```

## Deployment
- VPS: 155.212.226.75, отдельный порт (TBD)
- Nginx проксирует на localhost
- `.env` для API ключей (OPENAI_API_KEY, ANTHROPIC_API_KEY)

## Key patterns
- FastAPI + Jinja2 templates
- Без базы данных — одноразовый конвейер
- Временные аудиофайлы удаляются после транскрипции
- yt-dlp для YouTube, file upload для остального
- Whisper API для транскрипции (нарезка на части если > 25 MB)
- Claude API для саммари и генерации продуктов

## Project docs
- `PROJECT.md` — vision, features, decisions
