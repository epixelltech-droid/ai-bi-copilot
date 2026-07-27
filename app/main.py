from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes import router

app = FastAPI(title="AI BI Copilot", version="0.1.0")
app.include_router(router, prefix="/api")
UI_HTML = Path(__file__).with_name("ui").joinpath("index.html")


@app.get("/", response_class=HTMLResponse)
def home():
    return UI_HTML.read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"status":"ok"}
