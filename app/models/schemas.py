from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    user_id: str = "demo-user"
    source: Literal["auto", "sql", "powerbi", "rag"] = "auto"


class QueryArtifact(BaseModel):
    language: Literal["SQL", "DAX", "NONE"]
    query: str | None = None


class VisualizationSpec(BaseModel):
    enabled: bool = False
    kind: str | None = None
    title: str | None = None
    figure: dict[str, Any] | None = None
    reason: str | None = None


class ChatResponse(BaseModel):
    answer: str
    route: str
    artifact: QueryArtifact
    data: list[dict[str, Any]] = []
    sources: list[str] = []
    visualization: VisualizationSpec = Field(default_factory=VisualizationSpec)
    audit_id: str


class HistoryEntry(BaseModel):
    timestamp_epoch: float
    audit_id: str
    user_id: str
    question: str
    resolved_question: str | None = None
    route: str
    generated_query: str | None = None
    query_language: str | None = None
    status: str
    latency_ms: int
    row_count: int = 0
    source_count: int = 0
    used_memory: bool = False
    answer_preview: str | None = None
    hybrid_meta: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
