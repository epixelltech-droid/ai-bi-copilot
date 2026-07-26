from app.rag.retriever import answer_from_context, retrieve as retrieve_chunks


def retrieve(question: str, k: int = 3) -> list[dict]:
    chunks = retrieve_chunks(question, k=k)
    return [
        {
            "title": chunk["title"],
            "text": chunk["text"],
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"],
        }
        for chunk in chunks
    ]


def answer(question: str, k: int = 3) -> dict:
    chunks = retrieve_chunks(question, k=k)
    return answer_from_context(question, chunks)
