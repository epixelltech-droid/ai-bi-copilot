import re
import unicodedata

from app.rag.document_loader import chunk_documents, load_markdown_documents

STOPWORDS = {
    "a", "alors", "au", "aucun", "aucune", "aux", "avec", "ce", "ces", "comment",
    "dans", "de", "des", "du", "elle", "en", "entre", "est", "et", "la", "le",
    "les", "leur", "mais", "ne", "pas", "par", "pour", "que", "quel", "quelle",
    "quels", "quelles", "qu", "quoi", "sa", "se", "ses", "si", "son", "sur",
    "the", "to", "un", "une", "veut", "voici", "what",
}

TOKEN_EXPANSIONS = {
    "asp": ["average", "selling", "price"],
    "average": ["asp"],
    "selling": ["asp"],
    "marge": ["margin"],
    "marges": ["margin", "gross"],
    "gross": ["margin"],
    "profit": ["margin"],
    "ca": ["revenue", "chiffre", "affaires"],
    "chiffre": ["revenue"],
    "affaires": ["revenue"],
    "revenu": ["revenue"],
    "revenus": ["revenue"],
    "cout": ["cost"],
    "couts": ["cost"],
    "costs": ["cost"],
    "clients": ["customer"],
    "client": ["customer"],
    "customer": ["client"],
    "customers": ["client"],
    "produit": ["product"],
    "produits": ["product"],
    "product": ["produit"],
    "categorie": ["category"],
    "categories": ["category"],
    "category": ["categorie"],
    "pays": ["country"],
    "country": ["pays"],
    "mensuel": ["month"],
    "mois": ["month", "month_name"],
    "regle": ["rules"],
    "regles": ["rules"],
    "smb": ["segment"],
    "retail": ["segment"],
    "enterprise": ["segment"],
    "top": ["ranked", "rank", "ranking"],
    "meilleur": ["top"],
    "meilleurs": ["top"],
    "classe": ["ranked"],
    "classement": ["ranking"],
}

IMPORTANT_TOKENS = {
    "asp", "average", "business", "category", "cost", "country", "customer",
    "enterprise", "gross", "margin", "price", "product", "quantity", "retail",
    "revenue", "rules", "segment", "smb", "top",
}

INTENT_TOKENS = {
    "calcule", "comment", "definition", "definir", "definit", "difference",
    "dire", "formule", "signifie", "veut",
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

    if "margin" in normalized_question and "%" in question:
        answer = _build_definition_answer(question, chunks)
    elif "difference entre" in normalized_question:
        answer = _build_difference_answer(question, chunks)
    elif "top product" in normalized_question or ("top" in normalized_question and "produit" in normalized_question):
        answer = _build_business_rule_answer(chunks, "top product")
    elif "top customer" in normalized_question or ("top" in normalized_question and "client" in normalized_question):
        answer = _build_business_rule_answer(chunks, "top customer")
    elif "smb" in normalized_question:
        answer = _build_line_answer(chunks, "SMB")
    elif "enterprise" in normalized_question and "client" in normalized_question:
        answer = _build_enterprise_answer(chunks)
    elif "pays" in normalized_question or "country" in normalized_question:
        answer = _build_country_answer(chunks)
    elif any(pattern in normalized_question for pattern in ["que signifie", "definition"]):
        answer = _build_definition_answer(question, chunks)
    elif any(pattern in normalized_question for pattern in ["comment calcule", "formule", "calcule t on"]):
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
    content_question_tokens = question_tokens - INTENT_TOKENS
    if not content_question_tokens:
        return 0

    title_tokens = _expand_tokens(_tokenize(chunk["title"]))
    body_tokens = _expand_tokens(_tokenize(chunk["text"]))
    title_overlap = content_question_tokens & title_tokens
    body_overlap = content_question_tokens & body_tokens

    if not title_overlap and not body_overlap:
        return 0

    score = len(body_overlap) + (4 * len(title_overlap))

    important_overlap = content_question_tokens & body_tokens & IMPORTANT_TOKENS
    score += 2 * len(important_overlap)

    if content_question_tokens and title_tokens and content_question_tokens <= title_tokens:
        score += 4

    if "formula" in body_tokens and ("calcule" in question_tokens or "formula" in question_tokens):
        score += 3
    if "definition" in body_tokens and "definition" in question_tokens:
        score += 2
    if "rules" in body_tokens and "rules" in question_tokens:
        score += 2
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
    available_chunks = _merge_chunks(chunks, chunk_documents(load_markdown_documents()))
    preferred_chunk = _find_best_matching_chunk(question, available_chunks)
    ordered_chunks = (
        [preferred_chunk] + [chunk for chunk in available_chunks if chunk is not preferred_chunk]
        if preferred_chunk
        else available_chunks
    )

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
    normalized_question = _normalize_text(question)
    first_kpi, second_kpi = _extract_difference_terms(normalized_question)
    available_chunks = _merge_chunks(chunks, chunk_documents(load_markdown_documents()))
    first_chunk = _find_kpi_chunk(available_chunks, first_kpi)
    second_chunk = _find_kpi_chunk(available_chunks, second_kpi)

    if not first_chunk or not second_chunk:
        return _build_generic_answer(chunks)

    first_definition = _extract_labeled_value(first_chunk["text"], "Definition")
    second_definition = _extract_labeled_value(second_chunk["text"], "Definition")
    second_formula = _extract_labeled_value(second_chunk["text"], "Formula")

    parts = []
    if first_definition:
        parts.append(f"{_display_kpi_name(first_kpi)} : {first_definition}")
    if second_definition:
        parts.append(f"{_display_kpi_name(second_kpi)} : {second_definition}")
    if second_formula:
        formula_label = "Formule de la marge" if second_kpi == "margin" else "Formule"
        parts.append(f"{formula_label} : {second_formula}")
    return "\n\n".join(parts)


def _build_business_rule_answer(chunks: list[dict], keyword: str) -> str:
    for chunk in chunks:
        text = _strip_markdown(chunk["text"])
        for sentence in _split_sentences(text):
            if keyword in sentence.lower():
                return sentence
    return _build_generic_answer(chunks)


def _build_enterprise_answer(chunks: list[dict]) -> str:
    return _build_line_answer(chunks, "Enterprise") or _build_generic_answer(chunks)


def _build_country_answer(chunks: list[dict]) -> str:
    for chunk in chunks:
        text = _strip_markdown(chunk["text"])
        for sentence in _split_sentences(text):
            normalized = _normalize_text(sentence)
            if "country" in normalized and ("customer" in normalized or "dim_customer" in normalized):
                return sentence
    return _build_generic_answer(chunks)


def _build_line_answer(chunks: list[dict], keyword: str) -> str:
    all_matching_lines = []
    for chunk in chunks:
        text = _strip_markdown(chunk["text"])
        all_matching_lines.extend(
            line.strip("- ").strip()
            for line in text.splitlines()
            if keyword.lower() in line.lower()
        )

    precise_lines = [
        line
        for line in all_matching_lines
        if line.lower().startswith(f"`{keyword.lower()}`")
        or line.lower().startswith(f"{keyword.lower()} ")
        or line.lower().startswith(f"{keyword.lower()}:")
    ]
    if precise_lines:
        return precise_lines[0]
    if all_matching_lines:
        return all_matching_lines[0]
    return ""


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
    if "asp" in normalized_question or "average selling price" in normalized_question:
        return _find_chunk_by_title(chunks, "average selling price")
    if "margin" in normalized_question and "%" in question:
        return _find_chunk_with_percent(chunks, "margin")
    if "gross margin" in normalized_question:
        return _find_chunk_by_title(chunks, "gross margin")
    if "cost" in normalized_question:
        return _find_chunk_by_title(chunks, "cost")
    if "revenue" in normalized_question:
        return _find_chunk_by_title(chunks, "revenue")
    if "margin" in normalized_question or "marge" in normalized_question:
        return _find_chunk_by_title(chunks, "margin", exclude_title="margin %")
    return chunks[0] if chunks else None


def _extract_difference_terms(normalized_question: str) -> tuple[str, str]:
    supported = ["average selling price", "gross margin", "revenue", "margin", "cost", "quantity", "asp"]
    found = []
    for term in supported:
        index = normalized_question.find(term)
        if index >= 0:
            found.append((index, term))
    found.sort(key=lambda item: item[0])

    unique = []
    for _, term in found:
        canonical = "average selling price" if term == "asp" else term
        if canonical not in unique:
            unique.append(canonical)
    if len(unique) >= 2:
        return unique[0], unique[1]
    return "revenue", "margin"


def _find_kpi_chunk(chunks: list[dict], kpi_name: str) -> dict | None:
    if kpi_name == "margin":
        return _find_chunk_by_title(chunks, "margin", exclude_title="margin %")
    return _find_chunk_by_title(chunks, kpi_name)


def _display_kpi_name(kpi_name: str) -> str:
    names = {
        "average selling price": "Average Selling Price",
        "gross margin": "Gross Margin",
        "revenue": "Revenue",
        "margin": "Margin",
        "cost": "Cost",
        "quantity": "Quantity",
    }
    return names.get(kpi_name, kpi_name.title())


def _merge_chunks(primary_chunks: list[dict], secondary_chunks: list[dict]) -> list[dict]:
    merged = []
    seen = set()
    for chunk in primary_chunks + secondary_chunks:
        if chunk["chunk_id"] in seen:
            continue
        seen.add(chunk["chunk_id"])
        merged.append(chunk)
    return merged


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
