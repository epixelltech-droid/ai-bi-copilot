# Deployment Notes

This project can run locally with Python or inside Docker.

## Local Python

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/init_demo_db.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000/
```

## Docker

Build the image:

```powershell
docker build -t ai-bi-copilot .
```

Run the container:

```powershell
docker run --rm -p 8000:8000 ai-bi-copilot
```

Open:

```text
http://127.0.0.1:8000/
```

## Hybrid OpenAI Mode

OpenAI is optional. To avoid accidental cost, the hybrid mode is disabled by default.

To enable it locally, set these variables in `.env`:

```text
HYBRID_LLM_ENABLED=true
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Never commit `.env` or API keys.
