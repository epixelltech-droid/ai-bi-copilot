import json, time, uuid
from pathlib import Path

AUDIT_FILE = Path("data/audit.jsonl")

def new_audit_id() -> str:
    return str(uuid.uuid4())

def write_audit(audit_id, user_id, question, route, generated_query,
                status, latency_ms, row_count=0, error=None):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp_epoch": time.time(),
        "audit_id": audit_id,
        "user_id": user_id,
        "question": question,
        "route": route,
        "generated_query": generated_query,
        "status": status,
        "latency_ms": latency_ms,
        "row_count": row_count,
        "error": error,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
