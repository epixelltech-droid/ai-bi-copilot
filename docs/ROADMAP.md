# Roadmap

Last updated: 2026-07-26

## Current Status

The local V1 is already working.

Completed:

- FastAPI API
- LangGraph orchestration
- deterministic Router
- SQL Agent on the SQLite star schema
- Insight Agent with readable business answers
- local offline RAG
- dynamic schema metadata
- audit logging
- automated local tests
- Git initialization
- first documentation baseline

## Phase 1 - Stable Local V1

Status: completed

Scope delivered:

- local SQLite BI model
- `fact_sales`, `dim_customer`, `dim_product`, `dim_date`
- analytical question flow
- documentary question flow
- deterministic local behavior
- no required Internet access

## Phase 2 - Documentation And Presentation

Status: in progress

Next priorities:

- polish the main README for GitHub presentation
- enrich architecture documentation
- keep demo scenarios up to date
- maintain a simple documentation workflow for each change

## Phase 3 - Product Hardening

Status: next

Potential improvements:

- expand SQL coverage for more business questions
- improve Router coverage for more user phrasings
- refine RAG scoring and answer quality
- enrich audit information
- clean temporary local files more systematically

## Phase 4 - Portfolio / Showcase

Status: next

Possible deliverables:

- architecture diagram image
- project screenshots
- short demo script
- portfolio-ready GitHub homepage
- short presentation video

## Phase 5 - Future Optional V2

Status: optional later

Possible future extensions:

- Azure OpenAI
- SQL Server
- real Power BI integration
- DAX execution against a semantic model
- authentication and governance
- production deployment

## Guiding Principle

The project should stay simple and local unless a new step has a clear purpose.
