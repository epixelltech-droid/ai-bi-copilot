import re
import unicodedata

from app.rag.document_loader import chunk_documents, load_markdown_documents

STOPWORDS = {
    "a", "alors", "au", "aucun", "aucune", "aux", "avec", "ce", "ces", "comment",
    "dans", "de", "des", "du", "elle", "en", "entre", "est", "et", "la", "le",
    "les", "leur", "mais", "ne", "pas", "par", "pour", "que", "quel", "quelle",
    "quels", "quelles", "qu", "quoi", "sa", "se", "ses", "si", "son", "sur",
    "the", "to", "un", "une", "voici", "what",
}

TOKEN_EXPANSIONS = {
    "marge": ["margin"],
    "marges": ["margin"],
    "ca": ["revenue"],
    "chiffre": ["revenue"],
    "affaires": ["revenue"],
    "revenu": ["revenue"],
    "clients": ["customer"],
    "client": ["customer"],
    "produit": ["product"],
    "produits": ["product"],
    "categorie": ["category"],
    "categories": ["category"],
    "pays": ["country"],
    "mensuel": ["month"],
    "mois": ["month", "month_name"],
    "regle": ["rules"],
    "regles": ["rules"],
}


def retrieve(question: str, k: int = 3) -> list[dict]:
    chunks = chunk_documents(load_markdown_documents())
    question_tokens = _expand_tokens(_tokenize(question))
    scored_chunks = []

    for chunk in chunks:
        score = _score_chunk(question_tokens, chunk)
        if score > 0:
            scored_chunks.append((score, chunk))

    scored_chunks.sort(key=lambda item: (-item[0], item[1]["source"], item[1]["chunk_id"]))
    return [chunk for _, chunk in scored_chunks[:k]]


def answer_from_context(question: str, chunks: list[dict]) -> dict:
    if not chunks:
        return {
            "answer": "Je n'ai pas trouve cette information dans la base documentaire.",
            "sources": [],
        }

    normalized_question = _normalize_text(question)
    sources = _unique_sources(chunks)

    if "difference entre" in normalized_question:
        answer = _build_difference_answer(question, chunks)
    elif "top customer" in normalized_question:
        answer = _build_business_rule_answer(chunks, "top customer")
    elif "enterprise" in normalized_question and "client" in normalized_question:
        answer = _build_enterprise_answer(chunks)
    elif any(pattern in normalized_question for pattern in ["que signifie", "definition"]):
        answer = _build_definition_answer(question, chunks)
    elif any(pattern in normalized_question for pattern in ["comment calcule", "formule"]):
        answer = _build_formula_answer(chunks)
    else:
        answer = _build_generic_answer(chunks)

    if not answer:
        answer = "Je n'ai pas trouve cette information dans la base documentaire."
        sources = []

    return {
        "answer": answer,
        "sources": sources,
    }


def _score_chunk(question_tokens: set[str], chunk: dict) -> int:
    title_tokens = _expand_tokens(_tokenize(chunk["title"]))
    body_tokens = _expand_tokens(_tokenize(chunk["text"]))
    title_overlap = question_tokens & title_tokens
    body_overlap = question_tokens & body_tokens

    score = len(body_overlap) + (2 * len(title_overlap))
    if "formula" in body_tokens and ("calcule" in question_tokens or "formula" in question_tokens):
        score += 1
    return score


def _expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in list(tokens):
        for related in TOKEN_EXPANSIONS.get(token, []):
            expanded.add(related)
    return expanded


def _tokenize(text: str) -> set[str]:
    normalized = _normalize_text(text)
    words = re.findall(r"[a-z0-9_]+", normalized)
    return {word for word in words if len(word) > 1 and word not in STOPWORDS}


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text.lower())
    normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    cleaned = "".join(ch if ch.isalnum() else " " for ch in normalized)
    return " ".join(cleaned.split())


def _unique_sources(chunks: list[dict]) -> list[str]:
    sources = []
    for chunk in chunks:
        if chunk["source"] not in sources:
            sources.append(chunk["source"])
    return sources


def _build_definition_answer(question: str, chunks: list[dict]) -> str:
    preferred_chunk = _find_best_matching_chunk(question, chunks)
    ordered_chunks = [preferred_chunk] + [chunk for chunk in chunks if chunk is not preferred_chunk] if preferred_chunk else chunks

    for chunk in ordered_chunks:
        definition = _extract_labeled_value(chunk["text"], "Definition")
        formula = _extract_labeled_value(chunk["text"], "Formula")
        interpretation = _extract_labeled_value(chunk["text"], "Interpretation")
        if definition:
            parts = [definition]
            if formula:
                parts.append(f"Formule : {formula}")
            if interpretation:
                parts.append(interpretation)
            return "\n\n".join(parts)
    return _build_generic_answer(chunks)


def _build_formula_answer(chunks: list[dict]) -> str:
    for chunk in chunks:
        definition = _extract_labeled_value(chunk["text"], "Definition")
        formula = _extract_labeled_value(chunk["text"], "Formula")
        interpretation = _extract_labeled_value(chunk["text"], "Interpretation")
        if formula:
            parts = []
            if definition:
                parts.append(definition)
            parts.append(f"Formule : {formula}")
            if interpretation:
                parts.append(interpretation)
            return "\n\n".join(parts)
    return _build_generic_answer(chunks)


def _build_difference_answer(question: str, chunks: list[dict]) -> str:
    revenue_definition = ""
    margin_definition = ""
    margin_formula = ""
    preferred_margin_chunk = _find_chunk_by_title(chunks, "margin", exclude_title="margin %")
    preferred_revenue_chunk = _find_chunk_by_title(chunks, "revenue")

    for chunk in chunks:
        title = _normalize_text(chunk["title"])
        if preferred_revenue_chunk and chunk["chunk_id"] == preferred_revenue_chunk["chunk_id"]:
            revenue_definition = _extract_labeled_value(chunk["text"], "Definition")
        if preferred_margin_chunk and chunk["chunk_id"] == preferred_margin_chunk["chunk_id"]:
            margin_definition = _extract_labeled_value(chunk["text"], "Definition")
            margin_formula = _extract_labeled_value(chunk["text"], "Formula")

    parts = []
    if revenue_definition:
        parts.append(f"Revenue : {revenue_definition}")
    if margin_definition:
        parts.append(f"Margin : {margin_definition}")
    if margin_formula:
        parts.append(f"Formule de la marge : {margin_formula}")
    return "\n\n".join(parts)


def _build_business_rule_answer(chunks: list[dict], keyword: str) -> str:
    for chunk in chunks:
        text = _strip_markdown(chunk["text"])
        for sentence in _split_sentences(text):
            if keyword in sentence.lower():
                return sentence
    return _build_generic_answer(chunks)


def _build_enterprise_answer(chunks: list[dict]) -> str:
    for chunk in chunks:
        text = _strip_markdown(chunk["text"])
        lines = [line.strip("- ").strip() for line in text.splitlines() if "Enterprise" in line]
        if lines:
            return lines[0]
    return _build_generic_answer(chunks)


def _build_generic_answer(chunks: list[dict]) -> str:
    sentences = []
    for chunk in chunks:
        cleaned = _strip_markdown(chunk["text"])
        for sentence in _split_sentences(cleaned):
            if sentence and sentence not in sentences:
                sentences.append(sentence)
            if len(sentences) >= 3:
                return "\n\n".join(sentences[:3])
    return "\n\n".join(sentences[:3])


def _extract_labeled_value(text: str, label: str) -> str:
    pattern = re.compile(rf"{label}:\s*(.+)", re.IGNORECASE)
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            return _strip_markdown(match.group(1)).strip()
    return ""


def _strip_markdown(text: str) -> str:
    cleaned = text.replace("`", "")
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\-\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def _split_sentences(text: str) -> list[str]:
    normalized = text.replace("\n", " ")
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    return [part.strip() for part in parts if part.strip()]


def _find_best_matching_chunk(question: str, chunks: list[dict]) -> dict | None:
    normalized_question = _normalize_text(question)
    if "margin" in normalized_question and "%" in question:
        return _find_chunk_with_percent(chunks, "margin")
    if "revenue" in normalized_question:
        return _find_chunk_by_title(chunks, "revenue")
    if "margin" in normalized_question or "marge" in normalized_question:
        return _find_chunk_by_title(chunks, "margin", exclude_title="margin %")
    return chunks[0] if chunks else None


def _find_chunk_by_title(chunks: list[dict], title_value: str, exclude_title: str | None = None) -> dict | None:
    normalized_target = _normalize_text(title_value)
    raw_exclude = exclude_title.lower() if exclude_title else None
    for chunk in chunks:
        raw_title = chunk["title"].lower()
        normalized_title = _normalize_text(chunk["title"])
        if raw_exclude and raw_title == raw_exclude:
            continue
        if normalized_title == normalized_target:
            return chunk
    return None


def _find_chunk_with_percent(chunks: list[dict], title_keyword: str) -> dict | None:
    for chunk in chunks:
        raw_title = chunk["title"].lower()
        if title_keyword in raw_title and "%" in raw_title:
            return chunk
    return None
