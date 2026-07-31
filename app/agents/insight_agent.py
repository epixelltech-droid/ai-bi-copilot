import json
import re

from app.core.llm import llm_text

SYSTEM = '''
You are a senior BI analyst. Answer in French.
Use only the supplied rows and context.
Give the key business insight and never invent a cause.
Rewrite the local insight in a concise, natural, business-friendly style.
French only. Do not answer in English.
Keep it strictly grounded in the provided data.
'''


def build_insight(question: str, rows: list[dict], context: list[dict]) -> str:
    return build_insight_details(question, rows, context)["answer"]


def build_insight_details(question: str, rows: list[dict], context: list[dict]) -> dict[str, str]:
    if not rows:
        return {
            "answer": "Aucune donnee ne correspond a la requete.",
            "mode": "local_empty",
        }

    local_answer = _build_local_insight(question, rows, context)
    prompt = json.dumps(
        {
            "question": question,
            "rows": rows[:30],
            "context": context[:10],
            "local_answer": local_answer,
        },
        ensure_ascii=False,
        default=str,
    )
    result = llm_text(SYSTEM, prompt)
    if result:
        cleaned = result.strip()
        if cleaned and _looks_reasonably_french(cleaned):
            return {
                "answer": cleaned,
                "mode": "llm",
            }

    return {
        "answer": local_answer,
        "mode": "local",
    }


def _build_local_insight(question: str, rows: list[dict], context: list[dict]) -> str:
    first = rows[0]
    year = _extract_year(question)

    if len(rows) == 1 and "revenue" in first and len(first.keys()) == 1:
        return f"Le chiffre d'affaires total est de {_format_number(first['revenue'])}."

    if len(rows) == 1 and "margin" in first and len(first.keys()) == 1:
        return f"La marge totale est de {_format_number(first['margin'])}."

    if "country" in first and "revenue" in first and len(rows) == 2:
        return _build_country_comparison_insight(rows, "revenue", year)

    if "country" in first and "margin" in first and len(rows) == 2:
        return _build_country_comparison_insight(rows, "margin", year)

    if "country" in first and "revenue" in first:
        return _build_ranking_insight(rows, "country", "revenue", "Le pays", year)

    if "country" in first and "margin" in first:
        return _build_ranking_insight(rows, "country", "margin", "Le pays", year)

    if "segment" in first and "revenue" in first:
        return _build_ranking_insight(rows, "segment", "revenue", "Le segment", year)

    if "segment" in first and "margin" in first:
        return _build_ranking_insight(rows, "segment", "margin", "Le segment", year)

    if "product_name" in first and "quantity" in first:
        return _build_ranking_insight(rows, "product_name", "quantity", "Le produit", year)

    if "product_name" in first and "revenue" in first:
        return _build_ranking_insight(rows, "product_name", "revenue", "Le produit", year)

    if "product_name" in first and "margin" in first:
        return _build_ranking_insight(rows, "product_name", "margin", "Le produit", year)

    if "customer_name" in first and "revenue" in first:
        return _build_ranking_insight(rows, "customer_name", "revenue", "Le client", year)

    if "category" in first and "revenue" in first:
        return _build_ranking_insight(rows, "category", "revenue", "La categorie", year)

    if "category" in first and "margin" in first:
        return _build_ranking_insight(rows, "category", "margin", "La categorie", year)

    if "year" in first and "month" in first and "revenue" in first:
        return _build_time_insight(rows, "revenue")

    if "year" in first and "month" in first and "margin" in first:
        return _build_time_insight(rows, "margin")

    if "year" in first and "revenue" in first:
        return _build_year_insight(rows, "revenue")

    if "year" in first and "margin" in first:
        return _build_year_insight(rows, "margin")

    return f"La requete a retourne {len(rows)} ligne(s)."


def _build_ranking_insight(
    rows: list[dict],
    label_key: str,
    metric_key: str,
    subject: str,
    year: int | None = None,
) -> str:
    ordered_rows = sorted(rows, key=lambda row: row[metric_key], reverse=True)
    top_rows = ordered_rows[:3]
    metric_label = _metric_label(metric_key)
    period_suffix = f" en {year}" if year else ""

    if len(top_rows) == 1:
        leader = top_rows[0]
        return (
            f"{subject} {leader[label_key]} arrive en tete{period_suffix} "
            f"avec {_format_number(leader[metric_key])} de {metric_label}."
        )

    leader = top_rows[0]
    pieces = [
        f"{subject} {leader[label_key]} arrive en tete{period_suffix} avec {_format_number(leader[metric_key])} de {metric_label}."
    ]
    for row in top_rows[1:]:
        pieces.append(f"{row[label_key]} suit avec {_format_number(row[metric_key])}.")
    return " ".join(pieces)


def _build_time_insight(rows: list[dict], metric_key: str) -> str:
    ordered_rows = sorted(rows, key=lambda row: (row["year"], row["month"]))
    top_row = max(ordered_rows, key=lambda row: row[metric_key])
    low_row = min(ordered_rows, key=lambda row: row[metric_key])
    period_count = len(ordered_rows)
    metric_phrase = "Le chiffre d'affaires mensuel" if metric_key == "revenue" else "La marge mensuelle"

    return (
        f"{metric_phrase} atteint son maximum en {top_row['month_name']} {top_row['year']} "
        f"avec {_format_number(top_row[metric_key])}. "
        f"Le niveau le plus bas est observe en {low_row['month_name']} {low_row['year']} "
        f"avec {_format_number(low_row[metric_key])}. "
        f"L'analyse couvre {period_count} periode(s)."
    )


def _build_year_insight(rows: list[dict], metric_key: str) -> str:
    ordered_rows = sorted(rows, key=lambda row: row["year"])
    top_row = max(ordered_rows, key=lambda row: row[metric_key])
    metric_label = "chiffre d'affaires" if metric_key == "revenue" else "marge"
    return (
        f"La {metric_label} pour {top_row['year']} est de {_format_number(top_row[metric_key])}. "
        f"L'analyse couvre {len(ordered_rows)} annee(s)."
    )


def _build_country_comparison_insight(rows: list[dict], metric_key: str, year: int | None = None) -> str:
    ordered_rows = sorted(rows, key=lambda row: row[metric_key], reverse=True)
    leader = ordered_rows[0]
    follower = ordered_rows[1]
    gap = leader[metric_key] - follower[metric_key]
    metric_label = _metric_label(metric_key)
    period_suffix = f" en {year}" if year else ""

    return (
        f"{leader['country']} genere{period_suffix} {_format_number(leader[metric_key])} de {metric_label} contre "
        f"{_format_number(follower[metric_key])} pour {follower['country']}, "
        f"soit un ecart de {_format_number(gap)}."
    )


def _metric_label(metric_key: str) -> str:
    if metric_key == "revenue":
        return "chiffre d'affaires"
    if metric_key == "margin":
        return "marge"
    return "quantite"


def _extract_year(question: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", question)
    if match:
        return int(match.group(1))
    return None


def _format_number(value: float | int) -> str:
    formatted = f"{value:,.2f}"
    return formatted.replace(",", " ").replace(".", ",")


def _looks_reasonably_french(text: str) -> bool:
    normalized = f" {text.lower()} "
    french_cues = [" le ", " la ", " les ", " des ", " une ", " un ", " pour ", " avec ", " d'", " en "]
    english_cues = [" the ", " and ", " is ", " are ", " sales ", " generated ", " higher ", " business "]
    french_score = sum(1 for cue in french_cues if cue in normalized)
    english_score = sum(1 for cue in english_cues if cue in normalized)
    return french_score >= english_score
