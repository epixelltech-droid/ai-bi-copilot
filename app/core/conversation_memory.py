import re
import unicodedata
from threading import Lock
from typing import TypedDict


class ConversationTurn(TypedDict):
    question: str
    resolved_question: str
    route: str


MAX_TURNS = 6
_MEMORY: dict[str, list[ConversationTurn]] = {}
_LOCK = Lock()


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def clear_memory(user_id: str | None = None) -> None:
    with _LOCK:
        if user_id is None:
            _MEMORY.clear()
            return
        _MEMORY.pop(user_id, None)


def get_history(user_id: str) -> list[ConversationTurn]:
    with _LOCK:
        return list(_MEMORY.get(user_id, []))


def remember_turn(user_id: str, question: str, resolved_question: str, route: str) -> None:
    turn: ConversationTurn = {
        "question": question,
        "resolved_question": resolved_question,
        "route": route,
    }
    with _LOCK:
        history = _MEMORY.setdefault(user_id, [])
        history.append(turn)
        if len(history) > MAX_TURNS:
            del history[:-MAX_TURNS]


def resolve_question(user_id: str, question: str) -> tuple[str, list[ConversationTurn]]:
    history = get_history(user_id)
    if not history:
        return question, history

    normalized = normalize_text(question)
    if not _looks_like_follow_up(normalized):
        return question, history

    last_turn = history[-1]
    if last_turn["route"] == "sql":
        resolved = _resolve_sql_follow_up(question, normalized, last_turn["resolved_question"])
        return resolved or question, history

    if last_turn["route"] == "rag":
        resolved = _resolve_rag_follow_up(normalized)
        return resolved or question, history

    return question, history


def _looks_like_follow_up(normalized: str) -> bool:
    follow_up_prefixes = (
        "et ",
        "en 20",
        "par ",
        "compare ",
        "maintenant ",
        "du coup ",
        "alors ",
    )
    follow_up_phrases = {
        "2025",
        "2026",
        "par mois",
        "par pays",
        "par segment",
        "par categorie",
        "et la marge",
        "et le revenu",
        "et le revenue",
        "et le chiffre d affaires",
    }
    return normalized.startswith(follow_up_prefixes) or normalized in follow_up_phrases


def _resolve_sql_follow_up(question: str, normalized: str, base_question: str) -> str | None:
    base_normalized = normalize_text(base_question)
    year = _extract_year(normalized)
    dimension = _detect_dimension(base_normalized)
    metric = _detect_metric(base_normalized)

    if year and metric:
        return _build_metric_question(metric, dimension, year)

    if _asks_for_margin(normalized):
        return _build_metric_question("margin", dimension, _extract_year(base_normalized))

    if _asks_for_revenue(normalized):
        return _build_metric_question("revenue", dimension, _extract_year(base_normalized))

    requested_dimension = _detect_dimension(normalized)
    if requested_dimension and metric:
        return _build_metric_question(metric, requested_dimension, _extract_year(base_normalized))

    return None


def _resolve_rag_follow_up(normalized: str) -> str | None:
    if "margin %" in normalized or "marge %" in normalized:
        return "Que signifie Margin % ?"
    if "asp" in normalized:
        return "Comment calcule-t-on l'ASP ?"
    if "smb" in normalized:
        return "Que veut dire SMB ?"
    if "enterprise" in normalized:
        return "Qu'est-ce qu'un client Enterprise ?"
    if "top customer" in normalized:
        return "Comment definit-on un top customer ?"
    if "top product" in normalized:
        return "Comment est defini un top product ?"
    if "regle" in normalized:
        return "Quelles sont les regles metier ?"
    if "margin" in normalized or "marge" in normalized:
        return "Que signifie Margin ?"
    if "revenue" in normalized or "chiffre d affaires" in normalized:
        return "Que signifie Revenue ?"
    if "cost" in normalized or "cout" in normalized:
        return "Que signifie Cost ?"
    return None


def _extract_year(normalized: str) -> int | None:
    match = re.search(r"\b(20\d{2})\b", normalized)
    if not match:
        return None
    return int(match.group(1))


def _detect_metric(normalized: str) -> str | None:
    if _asks_for_margin(normalized):
        return "margin"
    if _asks_for_revenue(normalized):
        return "revenue"
    return None


def _asks_for_margin(normalized: str) -> bool:
    return "margin" in normalized or "marge" in normalized


def _asks_for_revenue(normalized: str) -> bool:
    revenue_terms = ("revenue", "ca", "chiffre d affaires", "chiffre d'affaire")
    return any(term in normalized for term in revenue_terms)


def _detect_dimension(normalized: str) -> str | None:
    if "par mois" in normalized or "mensuel" in normalized:
        return "par mois"
    if "par pays" in normalized or "country" in normalized:
        return "par pays"
    if "par segment" in normalized:
        return "par segment"
    if "par categorie" in normalized or "category" in normalized:
        return "par categorie"
    return None


def _build_metric_question(metric: str, dimension: str | None, year: int | None) -> str:
    if metric == "margin":
        if dimension == "par pays":
            question = "Quelle est la marge par pays"
        elif dimension == "par segment":
            question = "Quelle est la marge par segment"
        elif dimension == "par categorie":
            question = "Quelle est la marge par categorie"
        else:
            question = "Quelle est la marge"
    else:
        if dimension == "par pays":
            question = "Quel est le chiffre d'affaires par pays"
        elif dimension == "par segment":
            question = "Quel est le chiffre d'affaires par segment"
        elif dimension == "par categorie":
            question = "Quel est le chiffre d'affaires par categorie"
        elif dimension == "par mois":
            question = "Quel est le chiffre d'affaires par mois"
        else:
            question = "Quel est le chiffre d'affaires total"

    if year and dimension != "par mois":
        return f"{question} en {year} ?"
    return f"{question} ?"
