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

## Architecture Diagram

```mermaid
flowchart LR
    U[User Question] --> API[FastAPI API]
    API --> G[LangGraph]
    G --> R[Router]
    R --> SQL[SQL Agent]
    R --> RAG[RAG Agent]
    SQL --> GUARD[SQL Guard]
    GUARD --> DB[(SQLite Star Schema)]
    DB --> INSIGHT[Insight Agent]
    RAG --> KB[(Markdown Knowledge Base)]
    KB --> ANSWER[RAG Answer Builder]
    INSIGHT --> RESP[JSON Response]
    ANSWER --> RESP
    RESP --> AUDIT[Audit Log]
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

## Sample Questions

### Analytical questions

- `Quel est le chiffre d'affaires total ?`
- `Quel est le chiffre d'affaires par pays ?`
- `Quel est le top 5 des produits par chiffre d'affaires ?`
- `Quels sont les 10 meilleurs clients ?`
- `Quelle est la marge par categorie ?`
- `Quelle est la marge par pays en 2026 ?`
- `Quel est le chiffre d'affaires par mois ?`

### Documentary questions

- `Comment calcule-t-on la marge ?`
- `Que signifie Revenue ?`
- `Quelle est la difference entre Revenue et Margin ?`
- `Qu'est-ce qu'un client Enterprise ?`
- `Comment definit-on un top customer ?`
- `Quelles sont les regles metier ?`

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

## Example Outputs

### Example 1 - SQL insight

Question:

`Quel est le chiffre d'affaires par pays ?`

Typical answer:

`Le Maroc affiche le chiffre d'affaires le plus eleve, suivi de l'Italie puis de l'Espagne.`

### Example 2 - Documentary answer

Question:

`Comment calcule-t-on la marge ?`

Typical answer:

`La marge correspond a la difference entre le chiffre d'affaires et le cout. Formule : Margin = Revenue - Cost.`

## Demo Walkthrough

A simple demo flow for interviews or portfolio review:

1. open `http://127.0.0.1:8000/docs`
2. verify `GET /health`
3. test a SQL question such as `Quel est le chiffre d'affaires par pays ?`
4. test another SQL question such as `Quels sont les 10 meilleurs clients ?`
5. test a RAG question such as `Comment calcule-t-on la marge ?`
6. show that the RAG answer returns sources

Detailed walkthrough:

- `docs/DEMO_WALKTHROUGH.md`

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
- `docs/DEMO_WALKTHROUGH.md`
- `docs/PRODUCT_NEXT_STEPS.md`
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
