import json
import time
import uuid
from pathlib import Path

AUDIT_FILE = Path("data/audit.jsonl")


def new_audit_id() -> str:
    return str(uuid.uuid4())


def write_audit(
    audit_id,
    user_id,
    question,
    route,
    generated_query,
    status,
    latency_ms,
    row_count=0,
    error=None,
    resolved_question=None,
    query_language=None,
    source_count=0,
    used_memory=False,
    answer_preview=None,
    hybrid_meta=None,
):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_epoch": time.time(),
        "audit_id": audit_id,
        "user_id": user_id,
        "question": question,
        "resolved_question": resolved_question,
        "route": route,
        "generated_query": generated_query,
        "query_language": query_language,
        "status": status,
        "latency_ms": latency_ms,
        "row_count": row_count,
        "source_count": source_count,
        "used_memory": used_memory,
        "answer_preview": answer_preview,
        "hybrid_meta": hybrid_meta or {},
        "error": error,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_audit_entries(user_id: str | None = None, limit: int = 20) -> list[dict]:
    if not AUDIT_FILE.exists():
        return []

    entries = []
    with AUDIT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if user_id and entry.get("user_id") != user_id:
                continue
            entries.append(entry)

    entries.sort(key=lambda entry: entry.get("timestamp_epoch", 0), reverse=True)
    return entries[:limit]
