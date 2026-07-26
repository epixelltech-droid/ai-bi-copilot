from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.agents.dax_agent as dax_agent
import app.agents.insight_agent as insight_agent
import app.agents.sql_agent as sql_agent
import app.core.audit as audit_module
from app.main import app


@pytest.fixture(autouse=True)
def local_only_runtime(monkeypatch):
    monkeypatch.setattr(sql_agent, "llm_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(insight_agent, "llm_text", lambda *args, **kwargs: None)
    monkeypatch.setattr(dax_agent, "llm_text", lambda *args, **kwargs: None)
    audit_file = Path("data") / f"test-audit-{uuid4()}.jsonl"
    monkeypatch.setattr(audit_module, "AUDIT_FILE", audit_file)
    yield
    if audit_file.exists():
        audit_file.unlink()


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_sql_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]
    assert body["sources"] == []
    assert body["audit_id"]


def test_chat_rag_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Comment calcule-t-on la marge ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"]
    assert any(source in body["sources"] for source in ["kpi_dictionary.md", "business_rules.md"])
    assert body["audit_id"]


def test_chat_rag_enterprise_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Qu'est-ce qu'un client Enterprise ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert "data_dictionary.md" in body["sources"]


def test_chat_sql_top_products_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le top 5 des produits ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert body["sources"] == []


def test_chat_unknown_documentary_question_returns_safe_rag_answer(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Que signifie EBITDA ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"] == "Je n'ai pas trouve cette information dans la base documentaire."
    assert body["sources"] == []
