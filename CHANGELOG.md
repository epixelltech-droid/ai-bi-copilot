# Changelog

All notable changes to this project should be recorded in this file.

The format is intentionally simple for this local project.

## 2026-07-27

### Added

- Extended deterministic SQL coverage:
  - revenue by segment
  - margin by segment
  - revenue by category
  - top products by quantity
  - top Retail customers
  - revenue and margin filters for 2025 and 2026
  - revenue by country filtered by year
- Extended local RAG knowledge base:
  - Gross Margin
  - Average Selling Price / ASP
  - SMB, Retail, and Enterprise segment explanations
  - country and category analysis explanations
  - additional top product and date filtering business rules
- Added RAG tests for synonyms, short questions, unknown questions, and source validation.

### Updated

- Improved local RAG retrieval scoring with more BI synonyms and better keyword weighting.
- Improved RAG answer synthesis for KPI definitions, KPI differences, country explanations, segment definitions, and top product rules.
- Improved Router coverage for documentary formulations such as "que veut dire", "a quoi correspond", and "comment est defini".
- Added a lightweight local demo UI at `/` for testing the copilot without going through Swagger first.

## 2026-07-26

### Added

- Local Git repository initialized on `main`
- Base project documentation:
  - `docs/PROJECT_OVERVIEW.md`
  - `docs/TECHNICAL_DOCUMENTATION.md`
  - `docs/DOCUMENTATION_WORKFLOW.md`
- Architecture documentation:
  - `docs/ARCHITECTURE.md`

### Updated

- `README.md` improved as the main project entry point
- `docs/ROADMAP.md` aligned with the real state of the local V1
- `docs/DEMO_SCRIPT.md` aligned with the current SQL and RAG flows

### Current Project State

- local FastAPI API
- LangGraph orchestration
- SQLite star schema
- deterministic SQL Agent
- deterministic Insight Agent
- local offline RAG
- automated tests
- no required Internet dependency for local usage
