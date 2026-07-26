# Technical Documentation

## Stack

- Python
- FastAPI
- LangGraph
- SQLite
- Pytest

Optional code paths still exist for external integrations, but the current V1 runs locally without them.

## Entry Point

Main entry point:

- `app/main.py`

This file creates the FastAPI application and exposes the API routes.

## API Layer

Main route file:

- `app/api/routes.py`

Important endpoints:

- `GET /health`
- `POST /api/chat`

`POST /api/chat` receives a user question and returns:

- the chosen route
- the natural-language answer
- the SQL or artifact if relevant
- the returned data rows if relevant
- the audit id
- sources for RAG answers

## LangGraph Layer

Main graph file:

- `app/agents/graph.py`

Current logical flow:

1. START
2. Router node
3. SQL node or RAG node or Power BI node
4. END

The graph state stores the question, route, answer, rows, query, language, sources, and audit information.

## Router

Main file:

- `app/agents/router.py`

Role:

- classify a question as SQL, RAG, or Power BI

Current approach:

- deterministic rules
- simple keyword and phrase matching
- normalized text handling

## SQL Agent

Main file:

- `app/agents/sql_agent.py`

Role:

- convert analytical questions into SQLite read-only SQL

Current behavior:

- deterministic handling for common BI questions
- optional LLM path if configured
- uses schema metadata from `app/connectors/schema_metadata.py`
- always sends generated SQL through `validate_readonly_sql()`

## Insight Agent

Main file:

- `app/agents/insight_agent.py`

Role:

- turn raw SQL rows into short business-friendly answers

Current approach:

- deterministic formatting
- ranking summaries
- KPI summaries
- time-based summaries
- safe fallback when the returned structure is unknown

## Local RAG

Main files:

- `app/rag/document_loader.py`
- `app/rag/retriever.py`
- `app/rag/knowledge.py`

Role:

- answer documentary questions from local Markdown files

Current approach:

1. load `.md` files from `knowledge_base/`
2. split documents into chunks
3. score chunks with keyword matching
4. return top chunks
5. build a short deterministic answer from the retrieved context

No embeddings, no Internet, and no cloud model are required.

## SQLite Layer

Main files:

- `scripts/init_demo_db.py`
- `app/connectors/sqlite_demo.py`

Role:

- create and query the local BI demo database

Current data model:

- `fact_sales`
- `dim_customer`
- `dim_product`
- `dim_date`

## Metadata Layer

Main file:

- `app/connectors/schema_metadata.py`

Role:

- inspect SQLite dynamically
- list tables, columns, keys, and relations
- format the schema for the SQL Agent

This avoids hardcoding the business schema in Python.

## Audit Layer

Main file:

- `app/core/audit.py`

Role:

- persist a simple trace of user interactions

Typical audit content:

- user id
- question
- selected route
- generated query if any
- status
- timestamp or latency data

## Tests

Main test areas:

- API integration tests
- SQL Agent tests
- Router tests
- RAG tests
- database tests
- metadata tests
- Insight Agent tests

The project currently relies on local deterministic tests and does not require Internet access.
