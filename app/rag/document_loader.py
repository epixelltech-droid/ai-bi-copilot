from pathlib import Path

KNOWLEDGE_BASE_DIR = Path("knowledge_base")


def load_markdown_documents() -> list[dict]:
    documents = []
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        documents.append(
            {
                "source": path.name,
                "content": path.read_text(encoding="utf-8"),
            }
        )
    return documents


def chunk_documents(documents: list[dict], min_chunk_length: int = 80) -> list[dict]:
    chunks = []
    for document in documents:
        source = document["source"]
        sections = _split_markdown_sections(document["content"])
        for index, section in enumerate(sections, start=1):
            text = section["text"].strip()
            if len(text) < min_chunk_length and chunks:
                chunks[-1]["text"] = f"{chunks[-1]['text']}\n\n{text}".strip()
                continue
            chunks.append(
                {
                    "chunk_id": f"{source}:{index}",
                    "source": source,
                    "title": section["title"],
                    "text": text,
                }
            )
    return chunks


def _split_markdown_sections(content: str) -> list[dict]:
    sections = []
    current_title = "Document"
    current_lines = []

    for line in content.splitlines():
        if line.startswith("#"):
            if current_lines:
                sections.append(
                    {
                        "title": current_title,
                        "text": "\n".join(current_lines).strip(),
                    }
                )
            current_title = line.lstrip("#").strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        sections.append(
            {
                "title": current_title,
                "text": "\n".join(current_lines).strip(),
            }
        )

    return [section for section in sections if section["text"]]
