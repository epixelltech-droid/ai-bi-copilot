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
Prefer short, explicit SQLite queries with the correct GROUP BY, ORDER BY and LIMIT when useful.
Return SQL only.
'''


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKD", question.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def has_revenue_terms(text: str) -> bool:
    tokens = text.split()
    return contains_any(text, ["chiffre d'affaires", "chiffre d affaires", "revenue"]) or "ca" in tokens


def has_margin_terms(text: str) -> bool:
    return contains_any(text, ["marge", "margin"])


def has_customer_terms(text: str) -> bool:
    return contains_any(text, ["client", "clients", "customer", "customers"])


def has_product_terms(text: str) -> bool:
    return contains_any(text, ["produit", "produits", "product", "products"])


def has_top_terms(text: str) -> bool:
    return contains_any(text, ["top", "meilleur", "meilleurs", "plus performants", "performants", "plus vendu"])


def detect_year(text: str) -> int | None:
    if "2026" in text:
        return 2026
    if "2025" in text:
        return 2025
    return None


def detect_segment(text: str) -> str | None:
    if "enterprise" in text:
        return "Enterprise"
    if "retail" in text:
        return "Retail"
    if "smb" in text:
        return "SMB"
    return None


def detect_month(text: str) -> tuple[int, str] | None:
    months = {
        "janvier": (1, "janvier"),
        "fevrier": (2, "fevrier"),
        "mars": (3, "mars"),
        "avril": (4, "avril"),
        "mai": (5, "mai"),
        "juin": (6, "juin"),
        "juillet": (7, "juillet"),
        "aout": (8, "aout"),
        "septembre": (9, "septembre"),
        "octobre": (10, "octobre"),
        "novembre": (11, "novembre"),
        "decembre": (12, "decembre"),
    }
    for month_name, month_value in months.items():
        if month_name in text:
            return month_value
    return None


def deterministic_sql(question: str) -> str:
    q = normalize_question(question)
    year = detect_year(q)
    segment = detect_segment(q)
    month = detect_month(q)

    if month and year and contains_any(q, ["vente", "ventes"]):
        month_number, _ = month
        return f"""
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
WHERE d.year = {year}
  AND d.month = {month_number}
ORDER BY d.full_date DESC, f.revenue DESC
LIMIT 100
""".strip()

    if "france" in q and "maroc" in q and has_revenue_terms(q):
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

    if "france" in q and "maroc" in q and has_margin_terms(q):
        return """
SELECT
    c.country,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.country IN ('France', 'Maroc')
GROUP BY c.country
ORDER BY margin DESC
""".strip()

    if segment and has_customer_terms(q) and has_top_terms(q):
        return f"""
SELECT
    c.customer_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.segment = '{segment}'
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 10
""".strip()

    if "segment" in q and has_revenue_terms(q) and year:
        return f"""
SELECT
    c.segment,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY c.segment
ORDER BY revenue DESC
""".strip()

    if "segment" in q and has_margin_terms(q) and year:
        return f"""
SELECT
    c.segment,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY c.segment
ORDER BY margin DESC
""".strip()

    if ("categorie" in q or "category" in q) and has_revenue_terms(q) and year:
        return f"""
SELECT
    p.category,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY p.category
ORDER BY revenue DESC
""".strip()

    if ("categorie" in q or "category" in q or ("cat" in q and "gorie" in q)) and has_margin_terms(q) and year:
        return f"""
SELECT
    p.category,
    ROUND(SUM(f.margin), 2) AS margin
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY p.category
ORDER BY margin DESC
""".strip()

    if ("par mois" in q or "par month" in q or "mensuel" in q) and has_revenue_terms(q) and year:
        return f"""
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month
""".strip()

    if has_product_terms(q) and ("quantite" in q or "quantity" in q) and has_top_terms(q) and year:
        limit_clause = "LIMIT 5" if any(x in q for x in ["top 5", "top cinq", "cinq"]) else "LIMIT 1"
        return f"""
SELECT
    p.product_name,
    SUM(f.quantity) AS quantity
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
JOIN dim_date d
    ON f.date_id = d.date_id
WHERE d.year = {year}
GROUP BY p.product_name
ORDER BY quantity DESC
{limit_clause}
""".strip()

    if segment and has_revenue_terms(q):
        return f"""
SELECT
    c.segment,
    ROUND(SUM(f.revenue), 2) AS revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE c.segment = '{segment}'
GROUP BY c.segment
""".strip()

    if "retail" in q and has_customer_terms(q) and has_top_terms(q):
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

    if "segment" in q and has_margin_terms(q):
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

    if "segment" in q and has_revenue_terms(q):
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

    if has_margin_terms(q) and "pays" in q and "2026" in q:
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

    if ("pays" in q or "country" in q) and has_revenue_terms(q) and "2025" in q:
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

    if ("pays" in q or "country" in q) and has_revenue_terms(q) and "2026" in q:
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

    if has_revenue_terms(q) and "2025" in q:
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

    if has_margin_terms(q) and "2025" in q:
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

    if has_revenue_terms(q) and "2026" in q:
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

    if has_margin_terms(q) and "2026" in q:
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

    if has_margin_terms(q) and "pays" in q:
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

    if has_product_terms(q) and ("quantite" in q or "quantity" in q) and has_top_terms(q):
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

    if has_customer_terms(q) and any(x in q for x in ["10 meilleurs", "top 10", "top clients", "meilleurs clients"]):
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

    if has_customer_terms(q) and any(x in q for x in ["genere le plus", "plus de chiffre d'affaires", "plus de chiffre d affaires"]):
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

    if ("par mois" in q or "par month" in q or "mensuel" in q) and has_revenue_terms(q):
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

    if has_margin_terms(q) and ("categorie" in q or "category" in q or ("cat" in q and "gorie" in q)):
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

    if has_margin_terms(q) and has_product_terms(q):
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

    if ("categorie" in q or "category" in q) and has_revenue_terms(q):
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

    if has_product_terms(q) and has_top_terms(q) and has_revenue_terms(q):
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

    if ("pays" in q or "country" in q) and has_revenue_terms(q):
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

    if contains_any(q, ["chiffre d'affaires total", "chiffre d affaires total", "ca total", "revenue total"]):
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
    deterministic_query = deterministic_sql(question)
    schema_text = format_schema_for_llm()
    prompt = (
        f"SCHEMA:\n{schema_text}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"DETERMINISTIC_BASELINE:\n{deterministic_query}\n\n"
        "Return a better SQL query only if needed. "
        "If the baseline is already correct, you may return it unchanged."
    )
    query = llm_text(SYSTEM, prompt)
    if query:
        cleaned_query = query.replace("```sql", "").replace("```", "").strip()
        try:
            return validate_readonly_sql(cleaned_query)
        except ValueError:
            pass

    return validate_readonly_sql(deterministic_query)
