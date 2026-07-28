import time

from fastapi import APIRouter, HTTPException

from app.agents.graph import copilot_graph
from app.core.conversation_memory import remember_turn, resolve_question
from app.core.audit import new_audit_id, read_audit_entries, write_audit
from app.models.schemas import ChatRequest, ChatResponse, HistoryEntry, QueryArtifact

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    started = time.perf_counter()
    audit_id = new_audit_id()
    result = {}
    resolved_question, history = resolve_question(req.user_id, req.question)
    used_memory = resolved_question != req.question and bool(history)
    try:
        result = copilot_graph.invoke({
            "question": resolved_question,
            "preferred_source": req.source,
        })
        remember_turn(req.user_id, req.question, resolved_question, result["route"])
        latency = int((time.perf_counter() - started) * 1000)
        write_audit(
            audit_id,
            req.user_id,
            req.question,
            result["route"],
            result.get("query"),
            "success",
            latency,
            len(result.get("rows", [])),
            resolved_question=resolved_question,
            query_language=result.get("query_language", "NONE"),
            source_count=len(result.get("sources", [])),
            used_memory=used_memory,
            answer_preview=_answer_preview(result.get("answer", "")),
        )
        return ChatResponse(
            answer=result["answer"],
            route=result["route"],
            artifact=QueryArtifact(
                language=result.get("query_language", "NONE"),
                query=result.get("query"),
            ),
            data=result.get("rows", []),
            sources=result.get("sources", []),
            audit_id=audit_id,
        )
    except Exception as exc:
        latency = int((time.perf_counter() - started) * 1000)
        write_audit(
            audit_id,
            req.user_id,
            req.question,
            result.get("route", "unknown"),
            result.get("query"),
            "error",
            latency,
            error=str(exc),
            resolved_question=resolved_question,
            query_language=result.get("query_language"),
            source_count=len(result.get("sources", [])),
            used_memory=used_memory,
            answer_preview=_answer_preview(result.get("answer", "")),
        )
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/history/{user_id}", response_model=list[HistoryEntry])
def history(user_id: str, limit: int = 20):
    safe_limit = max(1, min(limit, 100))
    return [HistoryEntry(**entry) for entry in read_audit_entries(user_id=user_id, limit=safe_limit)]


def _answer_preview(answer: str, max_length: int = 160) -> str:
    compact = " ".join(answer.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3].rstrip() + "..."
