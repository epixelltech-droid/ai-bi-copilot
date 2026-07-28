# Roadmap

Last updated: 2026-07-27

## Current Status

The local V1 is already working.

Completed:

- FastAPI API
- LangGraph orchestration
- deterministic Router
- SQL Agent on the SQLite star schema
- Insight Agent with readable business answers
- local offline RAG
- enriched local knowledge base
- improved RAG retrieval scoring and answer quality
- expanded deterministic SQL coverage across segment, category, quantity, and year filters
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
- `116` passing local tests

## Phase 2 - Documentation And Presentation

Status: active

Next priorities:

- keep demo scenarios and screenshots up to date
- add one real product screenshot to the GitHub README
- maintain documentation updates together with code changes
- keep the public project presentation aligned with the current capabilities

## Phase 3 - Product Hardening

Status: next

Potential improvements:

- expand SQL coverage for more cross-filters and ranking cases
- improve Router coverage for more user phrasings
- continue refining RAG scoring and answer synthesis
- enrich audit information
- add a simple local demo UI

## Phase 4 - Portfolio / Showcase

Status: next

Possible deliverables:

- architecture diagram image
- project screenshots
- short demo script
- portfolio-ready GitHub homepage
- short presentation video

## Phase 5 - Future Optional V2

Status: active planning

Current direction:

- V2 will be built in small work lots, starting from the current local V1
- the first V2 lot is framing and perimeter definition
- the next implementation lot is conversation memory

Detailed scope:

- see [V2 Scope](C:/Users/Workspace/Documents/ai-bi-copilot-starter/ai-bi-copilot/docs/V2_SCOPE.md:1)

Longer-term possible extensions:

- Azure OpenAI
- SQL Server
- real Power BI integration
- DAX execution against a semantic model
- authentication and governance
- production deployment

## Guiding Principle

The project should stay simple and local unless a new step has a clear purpose.
