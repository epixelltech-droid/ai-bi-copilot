import json

from app.core.llm import llm_text

SYSTEM = '''
You are a senior BI analyst. Answer in French.
Use only the supplied rows and context.
Give the key business insight and never invent a cause.
'''


def build_insight(question: str, rows: list[dict], context: list[dict]) -> str:
    if not rows:
        return "Aucune donnée ne correspond à la requête."

    prompt = json.dumps({"question": question, "rows": rows[:30], "context": context},
                        ensure_ascii=False, default=str)
    result = llm_text(SYSTEM, prompt)
    if result:
        return result

    first = rows[0]

    if len(rows) == 1 and "revenue" in first and len(first.keys()) == 1:
        return f"Le chiffre d'affaires total est de {_format_number(first['revenue'])}."

    if "country" in first and "revenue" in first and len(rows) == 2:
        return _build_country_comparison_insight(rows)

    if "country" in first and "revenue" in first:
        return _build_ranking_insight(rows, "country", "revenue", "Le pays")

    if "country" in first and "margin" in first:
        return _build_ranking_insight(rows, "country", "margin", "Le pays")

    if "product_name" in first and "revenue" in first:
        return _build_ranking_insight(rows, "product_name", "revenue", "Le produit")

    if "customer_name" in first and "revenue" in first:
        return _build_ranking_insight(rows, "customer_name", "revenue", "Le client")

    if "category" in first and "margin" in first:
        return _build_ranking_insight(rows, "category", "margin", "La catégorie")

    if "year" in first and "month" in first and "revenue" in first:
        return _build_time_insight(rows)

    return f"La requête a retourné {len(rows)} ligne(s)."


def _build_ranking_insight(rows: list[dict], label_key: str, metric_key: str, subject: str) -> str:
    ordered_rows = sorted(rows, key=lambda row: row[metric_key], reverse=True)
    top_rows = ordered_rows[:3]
    metric_label = "chiffre d'affaires" if metric_key == "revenue" else "marge"

    if len(top_rows) == 1:
        leader = top_rows[0]
        return f"{subject} {leader[label_key]} arrive en tête avec {_format_number(leader[metric_key])} de {metric_label}."

    pieces = [
        f"{subject} {row[label_key]} arrive en tête avec {_format_number(row[metric_key])} de {metric_label}."
        if index == 0
        else f"{row[label_key]} suit avec {_format_number(row[metric_key])}."
        for index, row in enumerate(top_rows)
    ]
    return " ".join(pieces)


def _build_time_insight(rows: list[dict]) -> str:
    ordered_rows = sorted(rows, key=lambda row: (row["year"], row["month"]))
    top_row = max(ordered_rows, key=lambda row: row["revenue"])
    low_row = min(ordered_rows, key=lambda row: row["revenue"])
    period_count = len(ordered_rows)

    return (
        f"Le chiffre d'affaires mensuel atteint son maximum en {top_row['month_name']} {top_row['year']} "
        f"avec {_format_number(top_row['revenue'])}. "
        f"Le niveau le plus bas est observé en {low_row['month_name']} {low_row['year']} "
        f"avec {_format_number(low_row['revenue'])}. "
        f"L'analyse couvre {period_count} période(s)."
    )


def _build_country_comparison_insight(rows: list[dict]) -> str:
    ordered_rows = sorted(rows, key=lambda row: row["revenue"], reverse=True)
    leader = ordered_rows[0]
    follower = ordered_rows[1]
    gap = leader["revenue"] - follower["revenue"]

    return (
        f"{leader['country']} génère {_format_number(leader['revenue'])} contre "
        f"{_format_number(follower['revenue'])} pour {follower['country']}, "
        f"soit un écart de {_format_number(gap)}."
    )


def _format_number(value: float | int) -> str:
    formatted = f"{value:,.2f}"
    return formatted.replace(",", " ").replace(".", ",")
