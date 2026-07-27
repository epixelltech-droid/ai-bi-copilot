# Product Next Steps

## Goal

This document summarizes the most useful next evolutions for the project after the current local V1.

The idea is to stay pragmatic:

- improve what already exists
- avoid adding complexity too early
- keep the project demonstrable and understandable

## Priority 1 - Better Presentation

Why it matters:

- the project is already functional
- presentation now has a high impact for portfolio value

Recommended work:

- add a real screenshot of the running API or demo flow
- add one or two example outputs in visual form
- keep the README aligned with the current product state

## Priority 2 - Broader SQL Coverage

Why it matters:

- the SQL path is one of the most important parts of the project
- more supported business questions make the copilot more convincing

Recommended work:

- support more phrasings for existing questions
- support more filters such as year, segment, category, country
- enrich deterministic coverage before adding complexity

## Priority 3 - Stronger Router

Why it matters:

- the project depends on good routing between SQL and RAG

Recommended work:

- improve wording coverage
- reduce ambiguity for borderline questions
- keep the router deterministic and easy to understand

## Priority 4 - Better RAG Quality

Why it matters:

- the local RAG already works
- answer quality can still improve without changing the architecture too much

Recommended work:

- enrich the knowledge base
- improve chunk scoring
- improve answer synthesis while staying grounded

## Priority 5 - Simple User Interface

Why it matters:

- a small UI would make the project much easier to demonstrate

Recommended work:

- build a lightweight chat interface
- show route, answer, SQL, sources, and audit id
- keep the frontend minimal and local-first

## Priority 6 - Optional Future V2

Possible later directions:

- Azure OpenAI
- SQL Server
- real Power BI execution
- richer audit and observability
- authentication and governance

## Recommendation

The best next move is:

1. finish the portfolio presentation layer
2. strengthen the SQL and Router quality
3. only then move into a bigger V2
