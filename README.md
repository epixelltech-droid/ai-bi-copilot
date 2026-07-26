# AI BI Copilot

Local multi-agent BI copilot built with `FastAPI`, `LangGraph`, `SQLite`, and a lightweight offline `RAG`.

The goal is simple: let a user ask business questions in natural language and route the request to the right engine:

- `SQL` for analytical questions on structured data
- `RAG` for KPI definitions, business rules, and data documentation

This repository is designed as a clean, local-first portfolio project: readable, testable, and easy to run.

## Why This Project

Business users usually need two kinds of answers:

1. answers computed from data
2. answers grounded in business documentation

This project combines both in a single API flow.

Examples:

- `Quel est le chiffre d'affaires par pays ?`
- `Quels sont les 10 meilleurs clients ?`
- `Comment calcule-t-on la marge ?`
- `Quelle est la difference entre Revenue et Margin ?`

## What It Does

- routes each question to the right path
- generates read-only SQL for common BI questions
- executes queries on a local SQLite star schema
- transforms SQL rows into business-friendly insights
- retrieves documentation from a local Markdown knowledge base
- returns grounded documentary answers with sources
- logs each interaction in a simple audit trail

## Current Architecture

```text
POST /api/chat
  -> FastAPI
  -> LangGraph
  -> Router
     -> SQL Agent -> SQL Guard -> SQLite -> Insight Agent
     -> RAG Agent -> knowledge_base -> answer with sources
  -> JSON response
```

## Tech Stack

- Python
- FastAPI
- LangGraph
- SQLite
- Pytest
- local Markdown knowledge base

Optional integration code exists for Power BI / DAX, but the current V1 works fully locally.

## Key Capabilities

### 1. SQL analytics path

Supports deterministic local questions such as:

- total revenue
- revenue by country
- top products by revenue
- top customers
- revenue by month
- margin by category
- margin by country

### 2. Local RAG path

Supports documentary questions such as:

- KPI definitions
- business rules
- data model descriptions
- customer segment explanations

### 3. BI data model

The demo database uses a simple star schema:

- `fact_sales`
- `dim_customer`
- `dim_product`
- `dim_date`

### 4. Safe local execution

- read-only SQL validation
- no required Internet access
- no required cloud model
- no required Azure setup for local V1

## Example API Request

```json
{
  "question": "Quel est le chiffre d'affaires par pays ?",
  "user_id": "demo-user",
  "source": "auto"
}
```

## Example Response Types

### SQL route

```json
{
  "route": "sql",
  "answer": "Le Maroc affiche le chiffre d'affaires le plus eleve...",
  "sources": []
}
```

### RAG route

```json
{
  "route": "rag",
  "answer": "La marge correspond a la difference entre le chiffre d'affaires et le cout.",
  "sources": [
    "kpi_dictionary.md",
    "business_rules.md"
  ]
}
```

## Project Structure

```text
app/
  agents/        # router, SQL agent, insight agent, graph
  api/           # FastAPI routes
  connectors/    # SQLite, schema metadata, optional Power BI connector
  core/          # config, audit, optional LLM wrapper
  models/        # request / response schemas
  rag/           # loader, retriever, local RAG compatibility layer
  tools/         # SQL guardrails
knowledge_base/  # KPI, data dictionary, business rules
scripts/         # demo database initialization
tests/           # local automated tests
docs/            # project and technical documentation
```

## Run Locally

Recommended runtime: `Python 3.11`

### PowerShell

```powershell
Set-Location C:\path\to\ai-bi-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python scripts\init_demo_db.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

- `http://127.0.0.1:8000/docs`

Quick health check:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

If virtual environment activation is blocked, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/init_demo_db.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Local-Only Design

The current V1 is intentionally local-first:

- no Azure required
- no SQL Server required
- no Power BI environment required
- no Internet required for the main SQL and RAG flows

This makes the project easy to understand, test, and demonstrate.

## Documentation

- `docs/PROJECT_OVERVIEW.md`
- `docs/ARCHITECTURE.md`
- `docs/TECHNICAL_DOCUMENTATION.md`
- `docs/DOCUMENTATION_WORKFLOW.md`
- `docs/ROADMAP.md`
- `docs/DEMO_SCRIPT.md`
- `CHANGELOG.md`

## What Makes It Interesting

This project is a good showcase of:

- API design with FastAPI
- workflow orchestration with LangGraph
- deterministic agent design
- BI-oriented SQL generation
- star schema modeling
- offline RAG on local business documentation
- readable testing for a multi-agent local system

## Status

Current state:

- local V1 working
- SQL path working
- RAG path working
- automated tests in place
- GitHub repository initialized

## Notes

- This repository contains only local demo data and project documentation.
- No confidential production data is included.
- External integrations remain optional and are not required to run the local version.
