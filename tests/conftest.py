import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.conversation_memory import clear_memory
from app.agents import dax_agent, insight_agent, router as router_agent, sql_agent
from app.rag import retriever


def pytest_runtest_setup():
    clear_memory()


@pytest.fixture(autouse=True)
def local_only_llm_runtime(monkeypatch):
    monkeypatch.setattr(router_agent, "llm_json", lambda *args, **kwargs: None)
    monkeypatch.setattr(sql_agent, "llm_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(insight_agent, "llm_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(dax_agent, "llm_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(retriever, "llm_text", lambda *args, **kwargs: None)
