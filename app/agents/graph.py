from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.dax_agent import generate_dax
from app.agents.insight_agent import build_insight, build_insight_details
from app.agents.router import analyze_question
from app.agents.sql_agent import generate_sql, generate_sql_details
from app.connectors.powerbi import execute_dax
from app.connectors.sqlite_demo import execute_demo_sql
from app.rag.knowledge import retrieve
from app.rag.retriever import answer_from_context, retrieve as retrieve_chunks
from app.core.llm import get_llm_runtime_info
from app.visualization.plotly_builder import build_visualization


class CopilotState(TypedDict, total=False):
    original_question: str
    question: str
    preferred_source: str
    route: str
    context: list[dict]
    sources: list[str]
    query: str | None
    query_language: str
    rows: list[dict[str, Any]]
    answer: str
    visualization: dict[str, Any]
    hybrid_meta: dict[str, Any]


def router_node(state):
    analysis = analyze_question(state["question"], state.get("preferred_source", "auto"))
    original_question = state.get("original_question", state["question"])
    return {
        "route": analysis["route"],
        "question": analysis["rewritten_question"],
        "hybrid_meta": {
            "llm": get_llm_runtime_info(),
            "router_mode": analysis["mode"],
            "router_reason": analysis["reason"],
            "rewritten_by_router": analysis["rewritten_question"] != original_question,
            "original_question": original_question,
        },
    }


def rag_node(state):
    chunks = retrieve_chunks(state["question"], k=3)
    rag_result = answer_from_context(state["question"], chunks)
    return {
        "context": chunks,
        "sources": rag_result["sources"],
        "query": None,
        "query_language": "NONE",
        "rows": [],
        "answer": rag_result["answer"],
        "visualization": build_visualization(state["question"], []),
        "hybrid_meta": {
            **state.get("hybrid_meta", {}),
            "response_mode": rag_result.get("mode", "local"),
        },
    }


def sql_node(state):
    sql_result = generate_sql_details(state["question"])
    q = sql_result["query"]
    rows = execute_demo_sql(q)
    ctx = retrieve(state["question"])
    insight_result = build_insight_details(state["question"], rows, ctx)
    return {
        "context": ctx,
        "sources": [],
        "query": q,
        "query_language": "SQL",
        "rows": rows,
        "answer": insight_result["answer"],
        "visualization": build_visualization(state["question"], rows),
        "hybrid_meta": {
            **state.get("hybrid_meta", {}),
            "sql_generation_mode": sql_result["mode"],
            "response_mode": insight_result["mode"],
        },
    }


def powerbi_node(state):
    q = generate_dax(state["question"])
    ctx = retrieve(state["question"])
    try:
        rows = execute_dax(q)
        answer = build_insight(state["question"], rows, ctx)
    except RuntimeError:
        rows = []
        answer = "DAX genere. Configure POWERBI_DATASET_ID et POWERBI_ACCESS_TOKEN pour l'executer."
    return {
        "context": ctx,
        "sources": [],
        "query": q,
        "query_language": "DAX",
        "rows": rows,
        "answer": answer,
        "visualization": build_visualization(state["question"], rows),
    }


builder = StateGraph(CopilotState)
builder.add_node("router", router_node)
builder.add_node("rag", rag_node)
builder.add_node("sql", sql_node)
builder.add_node("powerbi", powerbi_node)
builder.add_edge(START, "router")
builder.add_conditional_edges("router", lambda s: s["route"], {"rag": "rag", "sql": "sql", "powerbi": "powerbi"})
builder.add_edge("rag", END)
builder.add_edge("sql", END)
builder.add_edge("powerbi", END)
copilot_graph = builder.compile()
