from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=4000)
    user_id: str = "demo-user"
    source: Literal["auto", "sql", "powerbi", "rag"] = "auto"


class QueryArtifact(BaseModel):
    language: Literal["SQL", "DAX", "NONE"]
    query: str | None = None


class ChatResponse(BaseModel):
    answer: str
    route: str
    artifact: QueryArtifact
    data: list[dict[str, Any]] = []
    sources: list[str] = []
    audit_id: str
