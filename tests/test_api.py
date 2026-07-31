from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import app.agents.dax_agent as dax_agent
import app.agents.insight_agent as insight_agent
import app.agents.router as router_agent
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


def test_home_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "AI BI Copilot" in response.text
    assert "Lancer" in response.text


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
    assert body["visualization"]["enabled"] is True
    assert body["visualization"]["kind"] == "bar"
    assert body["visualization"]["figure"]
    assert body["audit_id"]


def test_chat_sql_mode_uses_llm_router_rewrite_when_available(client, monkeypatch):
    monkeypatch.setattr(
        router_agent,
        "llm_json",
        lambda *args, **kwargs: {
            "route": "sql",
            "rewritten_question": "Quel est le chiffre d'affaires par pays ?",
            "reason": "normalized for analytics",
        },
    )

    response = client.post(
        "/api/chat",
        json={
            "question": "Montre moi le CA cote pays stp",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert body["data"]


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
    assert body["visualization"]["enabled"] is False
    assert body["audit_id"]


def test_history_endpoint_returns_recent_entries(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays ?",
            "user_id": "history-user",
            "source": "auto",
        },
    )
    second = client.post(
        "/api/chat",
        json={
            "question": "Comment calcule-t-on la marge ?",
            "user_id": "history-user",
            "source": "auto",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    response = client.get("/api/history/history-user")
    body = response.json()

    assert response.status_code == 200
    assert len(body) >= 2
    assert body[0]["user_id"] == "history-user"
    assert "question" in body[0]
    assert "resolved_question" in body[0]
    assert "query_language" in body[0]
    assert "source_count" in body[0]
    assert "answer_preview" in body[0]


def test_history_endpoint_shows_memory_usage(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays ?",
            "user_id": "history-memory-user",
            "source": "auto",
        },
    )
    second = client.post(
        "/api/chat",
        json={
            "question": "et en 2026 ?",
            "user_id": "history-memory-user",
            "source": "auto",
        },
    )

    assert first.status_code == 200
    assert second.status_code == 200

    response = client.get("/api/history/history-memory-user")
    body = response.json()

    assert response.status_code == 200
    assert body[0]["used_memory"] is True
    assert body[0]["resolved_question"] != body[0]["question"]
    assert "2026" in body[0]["resolved_question"]


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


def test_chat_sql_short_variant_routes_to_sql(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "CA par pays",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert body["answer"]


def test_chat_sql_monthly_variant_routes_to_sql(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "revenu mensuel",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert body["answer"]


def test_chat_sql_follow_up_year_uses_previous_question_context(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays ?",
            "user_id": "memory-user",
            "source": "auto",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={
            "question": "et en 2026 ?",
            "user_id": "memory-user",
            "source": "auto",
        },
    )

    body = second.json()

    assert second.status_code == 200
    assert body["route"] == "sql"
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert body["data"]


def test_chat_sql_follow_up_dimension_variant_uses_previous_metric(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires total ?",
            "user_id": "memory-user-2",
            "source": "auto",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={
            "question": "et par mois ?",
            "user_id": "memory-user-2",
            "source": "auto",
        },
    )

    body = second.json()

    assert second.status_code == 200
    assert body["route"] == "sql"
    assert "JOIN dim_date d" in body["artifact"]["query"]
    assert "d.month_name" in body["artifact"]["query"]
    assert body["data"]


def test_chat_sql_follow_up_metric_variant_uses_previous_dimension(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays ?",
            "user_id": "memory-user-3",
            "source": "auto",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={
            "question": "et la marge ?",
            "user_id": "memory-user-3",
            "source": "auto",
        },
    )

    body = second.json()

    assert second.status_code == 200
    assert body["route"] == "sql"
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert "SUM(f.margin)" in body["artifact"]["query"]
    assert body["data"]


def test_chat_rag_follow_up_uses_previous_documentary_context(client):
    first = client.post(
        "/api/chat",
        json={
            "question": "Que signifie Revenue ?",
            "user_id": "memory-user-4",
            "source": "auto",
        },
    )
    assert first.status_code == 200

    second = client.post(
        "/api/chat",
        json={
            "question": "et la marge ?",
            "user_id": "memory-user-4",
            "source": "auto",
        },
    )

    body = second.json()

    assert second.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"]
    assert any(source in body["sources"] for source in ["kpi_dictionary.md", "business_rules.md"])


def test_chat_rag_definition_variant_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "definition de margin",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"]


def test_chat_rag_c_est_quoi_variant_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "c'est quoi revenue",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"]


def test_chat_rag_asp_question_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Comment calcule-t-on l'ASP ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert "Revenue / Quantity" in body["answer"]
    assert "kpi_dictionary.md" in body["sources"]


def test_chat_rag_smb_question_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Que veut dire SMB ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert "SMB" in body["answer"]
    assert "data_dictionary.md" in body["sources"]


def test_chat_short_revenue_documentary_question_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Revenue ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert body["answer"]


def test_chat_enterprise_top_customers_routes_to_sql(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quels sont les clients Enterprise les plus performants ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert body["artifact"]["query"]
    assert "WHERE c.segment = 'Enterprise'" in body["artifact"]["query"]
    assert body["data"]


def test_chat_sql_revenue_by_segment_in_2026_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par segment en 2026 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert "JOIN dim_date d" in body["artifact"]["query"]
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert body["data"]


def test_chat_sql_revenue_by_month_in_2026_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par mois en 2026 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "JOIN dim_date d" in body["artifact"]["query"]
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert body["data"]


def test_chat_rag_top_product_question_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Comment est defini un top product ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert "top product" in body["answer"].lower()
    assert "business_rules.md" in body["sources"]


def test_chat_rag_country_question_routes_to_rag(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "A quoi correspond le pays dans les analyses ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "rag"
    assert body["artifact"]["language"] == "NONE"
    assert "customer" in body["answer"].lower() or "client" in body["answer"].lower()
    assert body["sources"]


def test_chat_sql_revenue_by_segment_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par segment ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_margin_by_segment_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quelle est la marge par segment ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "SUM(f.margin)" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_revenue_by_category_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par categorie ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "JOIN dim_product p" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_top_5_products_by_quantity_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le top 5 des produits en quantite ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "SUM(f.quantity) AS quantity" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_top_retail_customers_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quels sont les clients Retail les plus performants ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE c.segment = 'Retail'" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_revenue_for_2025_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires en 2025 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2025" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_revenue_for_2026_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires en 2026 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_revenue_by_country_for_2025_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays en 2025 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2025" in body["artifact"]["query"]
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_revenue_by_country_for_2026_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quel est le chiffre d'affaires par pays en 2026 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert "JOIN dim_customer c" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_margin_for_2025_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quelle est la marge en 2025 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2025" in body["artifact"]["query"]
    assert "SUM(f.margin)" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]


def test_chat_sql_margin_for_2026_mode(client):
    response = client.post(
        "/api/chat",
        json={
            "question": "Quelle est la marge en 2026 ?",
            "user_id": "test-user",
            "source": "auto",
        },
    )

    body = response.json()

    assert response.status_code == 200
    assert body["route"] == "sql"
    assert body["artifact"]["language"] == "SQL"
    assert "WHERE d.year = 2026" in body["artifact"]["query"]
    assert "SUM(f.margin)" in body["artifact"]["query"]
    assert body["data"]
    assert body["answer"]
