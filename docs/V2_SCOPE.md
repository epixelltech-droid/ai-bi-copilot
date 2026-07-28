# V2 Scope

Last updated: 2026-07-27

## Goal

V2 should make the copilot feel more natural, more reliable, and more product-like while keeping the current local-first architecture.

The V1 already proves that the project works:

- FastAPI API
- LangGraph orchestration
- deterministic Router
- SQL Agent on SQLite
- Insight Agent
- local offline RAG
- local UI
- automated tests

V2 is not a rewrite.
It is a controlled evolution of the current V1.

## V2 Product Objective

The target is a local BI assistant that can:

- understand a broader range of business questions
- keep short conversation context
- answer more naturally across follow-up questions
- produce more reliable business-oriented explanations
- remain fully testable and runnable locally

## What V2 Includes

The current V2 scope includes these workstreams:

1. conversation memory
2. Router improvements
3. SQL Agent improvements
4. Insight Agent improvements
5. RAG improvements
6. audit and traceability improvements
7. UI improvements for history and usability
8. UI improvements for result exploration

## What V2 Does Not Include

To keep V2 realistic and stable, these items are explicitly out of scope for now:

- Azure OpenAI dependency
- SQL Server migration
- real Power BI execution
- authentication
- multi-tenant security model
- cloud deployment
- vector database or embedding infrastructure
- complete NLP parser redesign

## V2 Principles

The implementation should follow these principles:

- keep the project local-first
- preserve the current V1 business flows
- improve by small lots of work
- add tests for each lot
- avoid large refactors without clear value
- keep the code readable for a beginner-friendly repository

## Target User Experience

Compared with V1, V2 should feel better in these situations:

- the user asks a follow-up question such as `et en 2026 ?`
- the user asks a shorter question that depends on previous context
- the user uses more varied wording for SQL questions
- the user expects a more polished business explanation
- the user wants clearer auditability of what happened

## Target Architecture

The global architecture stays the same:

```text
POST /api/chat
  -> FastAPI
  -> LangGraph
  -> Router
     -> SQL path
     -> RAG path
  -> JSON response
```

The main V2 evolution is not a new stack.
It is smarter behavior inside the current components.

## Planned Lots

### Lot 1 - V2 framing

Purpose:
- define the V2 perimeter
- align documentation
- fix the order of work

Expected result:
- a clear V2 scope document
- a consistent roadmap

### Lot 2 - Conversation memory

Purpose:
- support follow-up questions
- preserve short-term user context

Expected result:
- a simple local memory layer
- tests for contextual follow-up questions

### Lot 3 - Router V2

Purpose:
- improve route selection
- better recognize documentary vs analytical vs follow-up questions

Expected result:
- more robust deterministic routing

### Lot 4 - SQL Agent V2

Purpose:
- support more formulations and filters
- improve handling of realistic business requests

Expected result:
- broader deterministic SQL coverage

### Lot 5 - Insight Agent V2

Purpose:
- improve business readability of SQL results

Expected result:
- clearer and more helpful business summaries

### Lot 6 - RAG V2

Purpose:
- improve documentation retrieval and answer quality

Expected result:
- better keyword matching
- cleaner documentary answers

### Lot 7 - Audit and history

Purpose:
- improve traceability and debugging

Expected result:
- richer audit entries
- clearer local history behavior

### Lot 8 - UI V2

Purpose:
- expose conversation flow and improve usability

Expected result:
- local chat history
- cleaner response presentation
- better practical interaction

### Lot 9 - UI result exploration

Purpose:
- make SQL answers easier to read at a glance
- improve reuse of previous interactions

Expected result:
- quick result summary cards
- simple inline visual comparison for chart-friendly results
- clickable history items to replay or reuse questions

## Validation Rules For V2

Before a lot is considered complete:

- the existing V1 behavior must still work
- local tests must pass
- new tests must cover the new behavior
- documentation must be updated

## First Implementation Priority

The first real development lot after framing is:

`Lot 2 - Conversation memory`

Reason:
- it creates the strongest visible V2 improvement
- it improves both SQL and RAG experience
- it prepares the Router and SQL Agent for more natural follow-up questions
