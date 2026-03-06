"""Summarization and product generation via Claude API."""

import anthropic

MODEL = "claude-sonnet-4-20250514"


def summarize_transcript(transcript: str) -> str:
    """Create a structured summary from a transcript."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""Создай структурированное саммари этого транскрипта.

Формат:
## Тема
Одно предложение.

## Ключевые идеи
- Пронумерованный список главных мыслей (5-10 штук)

## Практические рекомендации
- Что можно применить прямо сейчас

## Цитаты
- Самые яркие фразы (если есть)

Транскрипт:
{transcript}""",
            }
        ],
    )
    return message.content[0].text


def generate_agent_prompt(summary: str) -> str:
    """Generate a system prompt for an AI agent based on the summary."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""На основе этого саммари создай системный промпт для ИИ-агента.

Агент должен быть экспертом в теме из саммари и помогать пользователю применять знания на практике.

Формат системного промпта:
1. Роль агента (кто он)
2. Его экспертиза (на основе ключевых идей)
3. Как он общается (стиль)
4. Что он делает (конкретные действия)
5. Ограничения (чего не делает)

Саммари:
{summary}""",
            }
        ],
    )
    return message.content[0].text
