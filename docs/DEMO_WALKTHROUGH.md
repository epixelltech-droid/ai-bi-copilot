# Demo Walkthrough

## Goal

This walkthrough helps present the project clearly during a demo, interview, or portfolio review.

The objective is to show:

1. the API is live
2. the SQL path works
3. the RAG path works
4. the project stays fully local for the current V1

## Suggested Demo Order

### 1. Show the API documentation

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`

What to say:

- the project now includes a lightweight local demo UI for quick product-style testing
- the project exposes a simple FastAPI interface
- the main endpoint is `POST /api/chat`
- the same endpoint can route to SQL or RAG depending on the question

### 2. Show the health endpoint

Request:

`GET /health`

Expected result:

```json
{
  "status": "ok"
}
```

What to say:

- the API is running locally
- this confirms the application is available before testing the main flow

### 3. Demo the SQL path

Use a question such as:

`Quel est le chiffre d'affaires par pays ?`

What to highlight:

- the Router selects the SQL path
- the SQL Agent generates a read-only query
- SQLite executes the query on the star schema
- the Insight Agent returns a business-friendly answer

What to mention:

- this is a local deterministic SQL flow
- no cloud dependency is required for this V1

### 4. Demo another analytical question

Use a question such as:

`Quel est le top 5 des produits en quantite ?`

What to highlight:

- a different business question is mapped to the same SQL path
- the SQL now supports quantity-based ranking in addition to revenue-based ranking
- the answer is not just raw rows, but a readable business summary

### 5. Demo a year-filtered analytical question

Use a question such as:

`Quel est le chiffre d'affaires en 2026 ?`

What to highlight:

- the SQL Agent understands a calendar filter
- the query uses `dim_date.year`
- the Insight Agent still returns a short business answer

### 6. Demo the RAG path

Use a question such as:

`Comment calcule-t-on l'ASP ?`

What to highlight:

- the Router selects the RAG path
- the retriever searches the local Markdown knowledge base
- the answer is grounded in documentation
- the API returns the answer with sources
- synonyms are supported, so `ASP` maps to `Average Selling Price`

### 7. Demo another documentary question

Use a question such as:

`Que veut dire SMB ?`

What to highlight:

- the answer comes from the data dictionary and business documentation
- short documentary questions are also handled
- no hallucinated value should be introduced

## Recommended Questions

### SQL

- `Quel est le chiffre d'affaires total ?`
- `Quel est le chiffre d'affaires par pays ?`
- `Quel est le chiffre d'affaires en 2026 ?`
- `Quel est le top 5 des produits par chiffre d'affaires ?`
- `Quel est le top 5 des produits en quantite ?`
- `Quelle est la marge par categorie ?`
- `Quels sont les 10 meilleurs clients ?`

### RAG

- `Comment calcule-t-on la marge ?`
- `Comment calcule-t-on l'ASP ?`
- `Que signifie Revenue ?`
- `Que veut dire SMB ?`
- `Quelle est la difference entre Revenue et Margin ?`
- `A quoi correspond le pays dans les analyses ?`
- `Comment est defini un top product ?`

## Short Presentation Script

Example:

`This project is a local AI BI Copilot built with FastAPI, LangGraph, SQLite, and an offline RAG. A user asks a business question in natural language, and the system routes it either to SQL for data analysis or to RAG for documentary answers. The current version is intentionally local, deterministic, and easy to test.`

## Key Message For Recruiters

This project demonstrates:

- API design
- agent orchestration
- BI-oriented SQL generation
- star schema usage
- local RAG over business documentation
- deterministic testing and documentation discipline
