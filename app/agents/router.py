import unicodedata


def normalize_question(question: str) -> str:
    normalized = unicodedata.normalize("NFKD", question.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def route_question(question: str, preferred: str = "auto") -> str:
    if preferred != "auto":
        return preferred

    q = normalize_question(question)

    documentary_patterns = [
        "definition",
        "definition de",
        "a quoi correspond",
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
        "difference entre",
        "diff rence entre",
        "top customer",
        "top product",
    ]

    if any(pattern in q for pattern in documentary_patterns):
        return "rag"

    if any(x in q for x in ["dax", "power bi", "semantic model", "mesure"]):
        return "powerbi"

    return "sql"
