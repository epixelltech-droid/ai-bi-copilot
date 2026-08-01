import app.agents.sql_agent as sql_agent
from app.connectors.sqlite_demo import execute_demo_sql


def run_local_sql(question: str, monkeypatch):
    monkeypatch.setattr(sql_agent, "llm_text", lambda *args, **kwargs: None)
    query = sql_agent.generate_sql(question)
    rows = execute_demo_sql(query)
    return query, rows


def test_llm_sql_can_be_used_when_valid(monkeypatch):
    monkeypatch.setattr(
        sql_agent,
        "llm_text",
        lambda *args, **kwargs: """
SELECT
    c.country,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.country
ORDER BY revenue DESC
""".strip(),
    )

    query = sql_agent.generate_sql("Montre moi le chiffre d'affaires par pays client")
    rows = execute_demo_sql(query)

    assert "JOIN dim_customer c" in query
    assert "SUM(f.revenue)" in query
    assert rows


def test_llm_sql_falls_back_to_deterministic_query_when_invalid(monkeypatch):
    monkeypatch.setattr(sql_agent, "llm_text", lambda *args, **kwargs: "DROP TABLE fact_sales")

    query = sql_agent.generate_sql("Quel est le chiffre d'affaires par pays ?")
    rows = execute_demo_sql(query)

    assert "DROP TABLE" not in query
    assert "JOIN dim_customer c" in query
    assert rows


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


def test_enterprise_top_customers_filters_segment(monkeypatch):
    query, rows = run_local_sql("Quels sont les clients Enterprise les plus performants ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "WHERE c.segment = 'Enterprise'" in query
    assert "GROUP BY c.customer_name" in query
    assert "LIMIT 10" in query
    assert len(rows) == 10
    assert "customer_name" in rows[0]
    assert "revenue" in rows[0]


def test_revenue_by_segment_in_2026_uses_segment_and_year(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par segment en 2026 ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert "GROUP BY c.segment" in query
    assert rows
    assert "segment" in rows[0]
    assert "revenue" in rows[0]


def test_margin_by_segment_in_2025_uses_segment_and_year(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par segment en 2025 ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2025" in query
    assert "GROUP BY c.segment" in query
    assert rows
    assert "segment" in rows[0]
    assert "margin" in rows[0]


def test_revenue_by_category_in_2026_uses_category_and_year(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par categorie en 2026 ?", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert "GROUP BY p.category" in query
    assert rows
    assert "category" in rows[0]
    assert "revenue" in rows[0]


def test_margin_by_category_in_2026_uses_category_and_year(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge par categorie en 2026 ?", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert "GROUP BY p.category" in query
    assert rows
    assert "category" in rows[0]
    assert "margin" in rows[0]


def test_revenue_by_month_in_2026_uses_month_and_year(monkeypatch):
    query, rows = run_local_sql("Quel est le chiffre d'affaires par mois en 2026 ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert "d.month_name" in query
    assert rows
    assert all(row["year"] == 2026 for row in rows)


def test_top_products_by_quantity_in_2026_uses_product_and_year(monkeypatch):
    query, rows = run_local_sql("Quel est le top 5 des produits en quantite en 2026 ?", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2026" in query
    assert "SUM(f.quantity) AS quantity" in query
    assert "LIMIT 5" in query
    assert len(rows) == 5


def test_compare_margin_between_france_and_maroc_filters_countries(monkeypatch):
    query, rows = run_local_sql("Compare la marge entre la France et le Maroc.", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "WHERE c.country IN ('France', 'Maroc')" in query
    assert "SUM(f.margin)" in query
    assert len(rows) == 2
    assert {row["country"] for row in rows} == {"France", "Maroc"}


def test_sales_for_january_2025_use_month_and_year(monkeypatch):
    query, rows = run_local_sql("Affiche les ventes de janvier 2025", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "WHERE d.year = 2025" in query
    assert "AND d.month = 1" in query
    assert rows
    assert "full_date" in rows[0]


def test_margin_percent_by_category_uses_grouped_margin_rate(monkeypatch):
    query, rows = run_local_sql("Quelle est la marge % par categorie ?", monkeypatch)

    assert "JOIN dim_product p" in query
    assert "SUM(f.margin) * 100.0 / NULLIF(SUM(f.revenue), 0)" in query
    assert "margin_pct" in query
    assert rows
    assert "category" in rows[0]
    assert "margin_pct" in rows[0]


def test_asp_by_country_uses_revenue_over_quantity(monkeypatch):
    query, rows = run_local_sql("Quel est l'ASP par pays ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "SUM(f.revenue) / NULLIF(SUM(f.quantity), 0)" in query
    assert "average_selling_price" in query
    assert rows
    assert "country" in rows[0]
    assert "average_selling_price" in rows[0]


def test_revenue_share_by_country_uses_window_total(monkeypatch):
    query, rows = run_local_sql("Quelle est la part du chiffre d'affaires par pays ?", monkeypatch)

    assert "JOIN dim_customer c" in query
    assert "SUM(SUM(f.revenue)) OVER ()" in query
    assert "revenue_share_pct" in query
    assert rows
    assert "country" in rows[0]
    assert "revenue_share_pct" in rows[0]


def test_revenue_evolution_by_year_uses_date_dimension(monkeypatch):
    query, rows = run_local_sql("Quelle est l'evolution du chiffre d'affaires par an ?", monkeypatch)

    assert "JOIN dim_date d" in query
    assert "GROUP BY d.year" in query
    assert rows
    assert {row["year"] for row in rows} == {2025, 2026}
