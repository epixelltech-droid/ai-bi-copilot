from app.agents.insight_agent import build_insight


def test_total_revenue_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    answer = build_insight("Quel est le chiffre d'affaires total ?", [{"revenue": 6044707.25}], [])

    assert "6 044 707,25" in answer
    assert "chiffre d'affaires total" in answer


def test_revenue_by_country_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"country": "Maroc", "revenue": 1325897.62},
        {"country": "Italie", "revenue": 1279942.73},
        {"country": "Allemagne", "revenue": 1170068.17},
    ]

    answer = build_insight("Quel est le chiffre d'affaires par pays ?", rows, [])

    assert "Maroc" in answer
    assert "1 325 897,62" in answer
    assert "Italie" in answer
    assert "due a" not in answer


def test_top_products_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"product_name": "Laptop Pro 14", "revenue": 1371348.68},
        {"product_name": "Laptop Air 13", "revenue": 1044131.46},
        {"product_name": "Desktop Mini", "revenue": 951214.55},
    ]

    answer = build_insight("Quel est le top 5 des produits par chiffre d'affaires ?", rows, [])

    assert "Laptop Pro 14" in answer
    assert "1 371 348,68" in answer


def test_top_customers_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"customer_name": "Summit Enterprise", "revenue": 281262.43},
        {"customer_name": "Pulse Enterprise", "revenue": 262094.85},
    ]

    answer = build_insight("Quels sont les 10 meilleurs clients ?", rows, [])

    assert "Summit Enterprise" in answer
    assert "281 262,43" in answer


def test_margin_by_category_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"category": "IT", "margin": 1401951.09},
        {"category": "Office", "margin": 445894.28},
    ]

    answer = build_insight("Quelle est la marge par categorie ?", rows, [])

    assert "IT" in answer
    assert "1 401 951,09" in answer


def test_margin_by_country_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"country": "Maroc", "margin": 300000},
        {"country": "France", "margin": 250000},
        {"country": "Italie", "margin": 200000},
    ]

    answer = build_insight("Quelle est la marge par pays ?", rows, [])

    assert "Maroc" in answer
    assert "300 000,00" in answer
    assert "marge" in answer.lower()
    assert "La requete a retourne" not in answer


def test_margin_by_country_2026_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"country": "Maroc", "margin": 240494.88},
        {"country": "Italie", "margin": 229457.20},
    ]

    answer = build_insight("Quelle est la marge par pays en 2026 ?", rows, [])

    assert "Maroc" in answer
    assert "240 494,88" in answer
    assert "marge" in answer.lower()
    assert "2026" in answer
    assert "La requete a retourne" not in answer


def test_revenue_by_month_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"year": 2025, "month": 1, "month_name": "January", "revenue": 168191.50},
        {"year": 2026, "month": 5, "month_name": "May", "revenue": 316077.11},
        {"year": 2026, "month": 2, "month_name": "February", "revenue": 178522.32},
    ]

    answer = build_insight("Quel est le chiffre d'affaires par mois ?", rows, [])

    assert "May 2026" in answer
    assert "316 077,11" in answer
    assert "January 2025" in answer
    assert "3 periode(s)" in answer


def test_france_maroc_comparison_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"country": "Maroc", "revenue": 1325897.62},
        {"country": "France", "revenue": 1117605.15},
    ]

    answer = build_insight("Compare le chiffre d'affaires entre la France et le Maroc.", rows, [])

    assert "Maroc genere 1 325 897,62" in answer
    assert "1 117 605,15 pour France" in answer
    assert "208 292,47" in answer


def test_no_result_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    answer = build_insight("Question", [], [])

    assert answer == "Aucune donnee ne correspond a la requete."


def test_unknown_result_shape_falls_back_safely(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [{"segment": "Enterprise", "count": 12}]
    answer = build_insight("Question", rows, [])

    assert answer == "La requete a retourne 1 ligne(s)."


def test_margin_by_category_2026_mentions_year(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"category": "IT", "margin": 621450.11},
        {"category": "Office", "margin": 205112.44},
    ]

    answer = build_insight("Quelle est la marge par categorie en 2026 ?", rows, [])

    assert "2026" in answer
    assert "IT" in answer
    assert "621 450,11" in answer


def test_enterprise_top_customers_insight(monkeypatch):
    monkeypatch.setattr("app.agents.insight_agent.llm_text", lambda *args, **kwargs: None)
    rows = [
        {"customer_name": "Summit Enterprise", "revenue": 281262.43},
        {"customer_name": "Pulse Enterprise", "revenue": 262094.85},
        {"customer_name": "Nova Enterprise", "revenue": 241100.12},
    ]

    answer = build_insight("Quels sont les clients Enterprise les plus performants ?", rows, [])

    assert "Summit Enterprise" in answer
    assert "281 262,43" in answer
    assert "Le client" in answer
