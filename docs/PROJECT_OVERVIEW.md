# Project Overview

## Goal

AI BI Copilot is a local multi-agent analytics assistant.

The goal is to let a user ask business questions in natural language and get either:

- a data answer produced from SQLite
- a documentation answer produced from the local knowledge base

This V1 is designed to stay simple, local, and understandable for a beginner.

## Main User Flows

### 1. Analytics question

Example:

`Quel est le chiffre d'affaires par pays ?`

Flow:

1. FastAPI receives the request.
2. The Router decides that the question is analytical.
3. LangGraph sends the request to the SQL Agent.
4. The SQL Agent generates a read-only SQLite query.
5. The query is validated by the SQL guardrail.
6. SQLite executes the query.
7. The Insight Agent turns rows into a business answer.
8. The audit trail stores the interaction.

### 2. Documentation question

Example:

`Comment calcule-t-on la marge ?`

Flow:

1. FastAPI receives the request.
2. The Router decides that the question is documentary.
3. LangGraph sends the request to the RAG node.
4. The local retriever searches the Markdown knowledge base.
5. The RAG answer builder creates a short grounded answer.
6. The API returns the answer with sources.
7. The audit trail stores the interaction.

## Current Functional Scope

- local FastAPI API
- local SQLite BI model
- star schema:
  - `fact_sales`
  - `dim_customer`
  - `dim_product`
  - `dim_date`
- deterministic SQL generation for common BI questions
- deterministic SQL coverage for segment, category, quantity, and year-filtered questions
- deterministic business insight generation
- local offline RAG over Markdown files
- improved local RAG over KPI definitions, business rules, and data dictionary content
- SQL safety validation
- audit logging
- automated tests

## What This Project Is Not Yet

At this stage, the project does not aim to be:

- a production-ready SaaS platform
- a full conversational BI product
- a cloud-integrated Azure architecture
- a real Power BI execution platform

It is a strong local V1 and a good base for a portfolio or a later V2.
