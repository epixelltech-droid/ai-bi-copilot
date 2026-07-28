from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.dax_agent import generate_dax
from app.agents.insight_agent import build_insight
from app.agents.router import route_question
from app.agents.sql_agent import generate_sql
from app.connectors.powerbi import execute_dax
from app.connectors.sqlite_demo import execute_demo_sql
from app.rag.knowledge import retrieve
from app.rag.retriever import answer_from_context, retrieve as retrieve_chunks
from app.visualization.plotly_builder import build_visualization


class CopilotState(TypedDict, total=False):
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


def router_node(state):
    return {"route": route_question(state["question"], state.get("preferred_source", "auto"))}


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
    }


def sql_node(state):
    q = generate_sql(state["question"])
    rows = execute_demo_sql(q)
    ctx = retrieve(state["question"])
    return {
        "context": ctx,
        "sources": [],
        "query": q,
        "query_language": "SQL",
        "rows": rows,
        "answer": build_insight(state["question"], rows, ctx),
        "visualization": build_visualization(state["question"], rows),
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
