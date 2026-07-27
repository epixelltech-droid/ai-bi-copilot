import app.agents.sql_agent as sql_agent
from app.connectors.sqlite_demo import execute_demo_sql


def run_local_sql(question: str, monkeypatch):
    monkeypatch.setattr(sql_agent, "llm_text", lambda *args, **kwargs: None)
    query = sql_agent.generate_sql(question)
    rows = execute_demo_sql(query)
    return query, rows


def test_total_revenue_query_uses_fact_sales(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires total ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "SUM(f.revenue)" in query
    assert len(rows) == 1
    assert rows[0]["revenue"] > 0


def test_revenue_by_country_uses_customer_dimension(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par pays ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_customer c" in query
    assert "c.country" in query
    assert rows
    assert "country" in rows[0]
    assert "revenue" in rows[0]


def test_top_5_products_uses_product_dimension(monkeypatch):
    query, rows = run_local_sql("Quel est le top 5 des produits par chiffre d'affaires ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_product p" in query
    assert "p.product_name" in query
    assert "LIMIT 5" in query
    assert len(rows) == 5


def test_top_5_products_by_quantity_uses_quantity_aggregation(monkeypatch):
    query, rows = run_local_sql("Quel est le top 5 des produits en quantite ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_product p" in query
    assert "SUM(f.quantity) AS quantity" in query
    assert "LIMIT 5" in query
    assert len(rows) == 5


def test_revenue_by_month_uses_date_dimension(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par mois ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_date d" in query
    assert "d.month_name" in query
    assert rows
    assert "year" in rows[0]
    assert "month" in rows[0]
    assert "month_name" in rows[0]


def test_top_customers_uses_customer_dimension(monkeypatch):
    query, rows = run_local_sql("Quels sont les 10 meilleurs clients par chiffre d'affaires ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_customer c" in query
    assert "c.customer_name" in query
    assert "LIMIT 10" in query
    assert len(rows) == 10


def test_top_retail_customers_filters_segment(monkeypatch):
    query, rows = run_local_sql("Quels sont les clients Retail les plus performants ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "WHERE c.segment = 'Retail'" in query
    assert "SUM(f.revenue)" in query
    assert len(rows) == 10
    assert "customer_name" in rows[0]
    assert "revenue" in rows[0]


def test_compare_france_and_maroc_filters_countries(monkeypatch):
    query, rows = run_local_sql("Compare le chiffre d'affaires entre la France et le Maroc.", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "WHERE c.country IN ('France', 'Maroc')" in query
    assert len(rows) == 2
    assert {row["country"] for row in rows} == {"France", "Maroc"}


def test_margin_by_country_in_2026_uses_date_filter(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par pays en 2026 ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert rows
    assert "margin" in rows[0]


def test_revenue_by_country_in_2025_uses_date_filter(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par pays en 2025 ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2025" in query
    assert rows
    assert "country" in rows[0]
    assert "revenue" in rows[0]


def test_revenue_by_country_in_2026_uses_date_filter(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par pays en 2026 ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert rows
    assert "country" in rows[0]
    assert "revenue" in rows[0]


def test_revenue_for_2025_uses_year_filter(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires en 2025 ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2025" in query
    assert len(rows) == 1
    assert rows[0]["year"] == 2025
    assert rows[0]["revenue"] > 0


def test_revenue_for_2026_uses_year_filter(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires en 2026 ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert len(rows) == 1
    assert rows[0]["year"] == 2026
    assert rows[0]["revenue"] > 0


def test_margin_for_2025_uses_year_filter(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge en 2025 ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2025" in query
    assert len(rows) == 1
    assert rows[0]["year"] == 2025
    assert rows[0]["margin"] > 0


def test_margin_for_2026_uses_year_filter(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge en 2026 ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert len(rows) == 1
    assert rows[0]["year"] == 2026
    assert rows[0]["margin"] > 0


def test_enterprise_revenue_filters_segment(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires des clients Enterprise ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "WHERE c.segment = 'Enterprise'" in query
    assert len(rows) == 1
    assert rows[0]["segment"] == "Enterprise"


def test_revenue_by_segment_uses_customer_segment(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par segment ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_customer c" in query
    assert "c.segment" in query
    assert "SUM(f.revenue)" in query
    assert rows
    assert "segment" in rows[0]
    assert "revenue" in rows[0]


def test_margin_by_segment_uses_customer_segment(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par segment ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_customer c" in query
    assert "c.segment" in query
    assert "SUM(f.margin)" in query
    assert rows
    assert "segment" in rows[0]
    assert "margin" in rows[0]


def test_revenue_by_category_uses_product_category(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par categorie ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_product p" in query
    assert "p.category" in query
    assert "SUM(f.revenue)" in query
    assert rows
    assert "category" in rows[0]
    assert "revenue" in rows[0]


def test_margin_by_category_uses_product_dimension(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par categorie ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_product p" in query
    assert "SUM(f.margin)" in query
    assert "p.category" in query
    assert rows
    assert "category" in rows[0]
    assert "margin" in rows[0]


def test_margin_by_category_short_form_uses_product_dimension(monkeypatch):
    query, rows = run_local_sql("Marge par categorie", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "SUM(f.margin)" in query
    assert rows


def test_margin_by_category_english_keyword_uses_product_dimension(monkeypatch):
    query, rows = run_local_sql("Margin par categorie", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "SUM(f.margin)" in query
    assert rows


def test_margin_by_country_uses_customer_dimension(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par pays ?", monkeypatch)

    assert "FROM fact_sales f" in query
    assert "JOIN dim_customer c" in query
    assert "SUM(f.margin)" in query
    assert "c.country" in query
    assert rows
    assert "country" in rows[0]
    assert "margin" in rows[0]
