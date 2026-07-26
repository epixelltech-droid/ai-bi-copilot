import time

from fastapi import APIRouter, HTTPException

from app.agents.graph import copilot_graph
from app.core.audit import new_audit_id, write_audit
from app.models.schemas import ChatRequest, ChatResponse, QueryArtifact

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    started = time.perf_counter()
    audit_id = new_audit_id()
    result = {}
    try:
        result = copilot_graph.invoke({
            "question": req.question,
            "preferred_source": req.source,
        })
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
        )
        raise HTTPException(status_code=400, detail=str(exc))
