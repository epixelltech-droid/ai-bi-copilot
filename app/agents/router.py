import unicodedata

from app.core.llm import llm_json

ROUTES = {"sql", "rag", "powerbi"}

ROUTER_SYSTEM = """
You are the routing layer of a BI copilot.
Choose exactly one route:
- sql: analytical question about metrics, dimensions, filters, ranking, trend, comparison, totals
- rag: documentary question about KPI definitions, business rules, data dictionary, terminology
- powerbi: explicit DAX / Power BI modeling request

Return strict JSON only with:
{
  "route": "sql|rag|powerbi",
  "rewritten_question": "clear canonical rewrite in French",
  "reason": "short reason"
}

The rewritten question must preserve the user's intent and help downstream SQL generation.
""".strip()


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKD", question.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def contains_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def is_powerbi_question(normalized_question: str) -> bool:
    return contains_any(normalized_question, ["dax", "power bi", "semantic model", "mesure"])


def is_documentary_question(normalized_question: str) -> bool:
    documentary_patterns = [
        "definition",
        "definition de",
        "a quoi correspond",
        "correspond a quoi",
        "que signifie",
        "que veut dire",
        "qu est ce",
        "quest ce",
        "c est quoi",
        "c quoi",
        "comment calcule",
        "comment definit",
        "comment definit on",
        "comment est defini",
        "definit on",
        "regle metier",
        "regles metier",
        "documentation",
        "explique moi",
    ]
    if contains_any(normalized_question, documentary_patterns):
        return True

    if "difference entre" in normalized_question or "diff rence entre" in normalized_question:
        analytical_entities = [
            "france",
            "maroc",
            "italie",
            "espagne",
            "allemagne",
            "pays",
            "segment",
            "categorie",
            "category",
            "client",
            "customer",
            "produit",
            "product",
            "2025",
            "2026",
        ]
        if contains_any(normalized_question, analytical_entities):
            return False
        return True

    documentary_short_forms = [
        "revenue",
        "margin",
        "margin %",
        "gross margin",
        "cost",
        "asp",
        "average selling price",
        "smb",
        "top customer",
        "top product",
    ]
    if normalized_question in documentary_short_forms:
        return True

    short_documentary_questions = [
        "que signifie revenue",
        "que signifie margin",
        "que signifie margin %",
        "que signifie cost",
        "que signifie asp",
        "que signifie smb",
    ]
    return normalized_question in short_documentary_questions


def is_analytical_question(normalized_question: str) -> bool:
    analytical_patterns = [
        "chiffre d affaires",
        "revenue",
        "ca",
        "ventes",
        "marge",
        "margin",
        "margin pct",
        "gross margin",
        "asp",
        "average selling price",
        "prix moyen",
        "part du",
        "contribution",
        "evolution",
        "variation",
        "croissance",
        "par pays",
        "par segment",
        "par categorie",
        "par mois",
        "par an",
        "annee",
        "mensuel",
        "top 5",
        "top 10",
        "meilleurs clients",
        "plus performants",
        "clients retail",
        "clients enterprise",
        "compare",
        "comparaison",
        "janvier 2026",
        "2025",
        "2026",
        "total",
    ]
    return contains_any(normalized_question, analytical_patterns)


def _deterministic_route(question: str) -> str:
    q = normalize_question(question)

    if is_powerbi_question(q):
        return "powerbi"

    if is_documentary_question(q):
        return "rag"

    if is_analytical_question(q):
        return "sql"

    return "sql"


def analyze_question(question: str, preferred: str = "auto") -> dict[str, str]:
    if preferred != "auto":
        return {
            "route": preferred,
            "rewritten_question": question,
            "reason": "preferred source",
            "mode": "preferred",
        }

    llm_result = llm_json(ROUTER_SYSTEM, question)
    if llm_result:
        route = str(llm_result.get("route", "")).strip().lower()
        rewritten_question = str(llm_result.get("rewritten_question", "")).strip() or question
        reason = str(llm_result.get("reason", "")).strip() or "llm route"
        if route in ROUTES:
            return {
                "route": route,
                "rewritten_question": rewritten_question,
                "reason": reason,
                "mode": "llm",
            }

    return {
        "route": _deterministic_route(question),
        "rewritten_question": question,
        "reason": "deterministic fallback",
        "mode": "deterministic",
    }


def route_question(question: str, preferred: str = "auto") -> str:
    return analyze_question(question, preferred)["route"]
