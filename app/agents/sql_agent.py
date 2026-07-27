import unicodedata

from app.connectors.schema_metadata import format_schema_for_llm
from app.core.llm import llm_text
from app.tools.sql_guard import validate_readonly_sql

SYSTEM = '''
You are a senior BI SQL analyst.
Generate ONE read-only SQLite query.
Use only the supplied tables, columns, and relations.
Use the provided joins when a dimension is needed.
Never use INSERT, UPDATE, DELETE, DROP, ALTER, EXEC or CREATE.
Return SQL only.
'''


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKD", question.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def deterministic_sql(question: str) -> str:
    q = normalize_question(question)

    if "janvier 2026" in q:
        return """
SELECT
    d.full_date,
    c.customer_name,
    c.country,
    p.product_name,
    p.category,
    f.quantity,
    f.unit_price,
    f.revenue,
    f.margin
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_product p
    ON f.product_id = p.product_id
WHERE d.year = 2026
  AND d.month = 1
ORDER BY d.full_date DESC, f.revenue DESC
LIMIT 100
""".strip()

    if "france" in q and "maroc" in q and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    c.country,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.country IN ('France', 'Maroc')
GROUP BY c.country
ORDER BY revenue DESC
""".strip()

    if "enterprise" in q and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    c.segment,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.segment = 'Enterprise'
GROUP BY c.segment
""".strip()

    if "retail" in q and any(x in q for x in ["client", "clients", "customer", "customers"]) and any(
        x in q for x in ["plus performants", "meilleurs", "top", "performants"]
    ):
        return """
SELECT
    c.customer_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.segment = 'Retail'
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 10
""".strip()

    if "segment" in q and ("marge" in q or "margin" in q):
        return """
SELECT
    c.segment,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY margin DESC
""".strip()

    if "segment" in q and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    c.segment,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.segment
ORDER BY revenue DESC
""".strip()

    if ("marge" in q or "margin" in q) and "pays" in q and "2026" in q:
        return """
SELECT
    c.country,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2026
GROUP BY c.country
ORDER BY margin DESC
""".strip()

    if ("pays" in q or "country" in q) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]) and "2025" in q:
        return """
SELECT
    c.country,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2025
GROUP BY c.country
ORDER BY revenue DESC
""".strip()

    if ("pays" in q or "country" in q) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]) and "2026" in q:
        return """
SELECT
    c.country,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2026
GROUP BY c.country
ORDER BY revenue DESC
""".strip()

    if any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]) and "2025" in q:
        return """
SELECT
    d.year,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2025
GROUP BY d.year
""".strip()

    if ("marge" in q or "margin" in q) and "2025" in q:
        return """
SELECT
    d.year,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2025
GROUP BY d.year
""".strip()

    if any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]) and "2026" in q:
        return """
SELECT
    d.year,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2026
GROUP BY d.year
""".strip()

    if ("marge" in q or "margin" in q) and "2026" in q:
        return """
SELECT
    d.year,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = 2026
GROUP BY d.year
""".strip()

    if ("marge" in q or "margin" in q) and "pays" in q:
        return """
SELECT
    c.country,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.country
ORDER BY margin DESC
""".strip()

    if ("produit" in q or "product" in q) and ("quantite" in q or "quantity" in q) and any(x in q for x in ["plus vendu", "meilleur", "top"]):
        limit_clause = "LIMIT 5" if any(x in q for x in ["top 5", "top cinq", "cinq"]) else "LIMIT 1"
        return f"""
SELECT
    p.product_name,
    SUM(f.quantity) AS quantity
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY quantity DESC
{limit_clause}
""".strip()

    if ("client" in q or "customers" in q or "customer" in q) and any(x in q for x in ["10 meilleurs", "top 10", "top clients", "meilleurs clients"]):
        return """
SELECT
    c.customer_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 10
""".strip()

    if ("client" in q or "customer" in q) and any(x in q for x in ["genere le plus", "plus de chiffre d'affaires", "plus de chiffre d affaires"]):
        return """
SELECT
    c.customer_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 1
""".strip()

    if ("par mois" in q or "par month" in q or "mensuel" in q) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
""".strip()

    if ("marge" in q or "margin" in q) and (
        "categorie" in q
        or "category" in q
        or ("cat" in q and "gorie" in q)
    ):
        return """
SELECT
    p.category,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY margin DESC
""".strip()

    if ("marge" in q or "margin" in q) and ("produit" in q or "product" in q):
        return """
SELECT
    p.product_name,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY margin DESC
LIMIT 20
""".strip()

    if ("categorie" in q or "category" in q) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.category
ORDER BY revenue DESC
""".strip()

    if ("produit" in q or "product" in q) and any(x in q for x in ["top 5", "top cinq", "top", "meilleur"]) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    p.product_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
GROUP BY p.product_name
ORDER BY revenue DESC
LIMIT 5
""".strip()

    if ("pays" in q or "country" in q) and any(x in q for x in ["chiffre d'affaires", "chiffre d affaires", "ca", "revenue"]):
        return """
SELECT
    c.country,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
GROUP BY c.country
ORDER BY revenue DESC
""".strip()

    if any(x in q for x in ["chiffre d'affaires total", "chiffre d affaires total", "ca total", "revenue total"]):
        return """
SELECT
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
""".strip()

    return """
SELECT
    d.full_date,
    c.country,
    p.product_name,
    f.quantity,
    f.revenue,
    f.margin
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_product p
    ON f.product_id = p.product_id
ORDER BY d.full_date DESC, f.sale_id DESC
LIMIT 20
""".strip()


def generate_sql(question: str) -> str:
    schema_text = format_schema_for_llm()
    prompt = f"SCHEMA:\n{schema_text}\n\nQUESTION:\n{question}"
    query = llm_text(SYSTEM, prompt) or deterministic_sql(question)
    query = query.replace("```sql", "").replace("```", "").strip()
    return validate_readonly_sql(query)
