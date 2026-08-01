# Improvement Batch

This document summarizes the latest product improvement batch.

## Goal

Make the AI BI Copilot more useful as a local BI assistant:

- better Router and SQL Agent understanding
- stronger local RAG knowledge
- richer business insights
- clearer visualization behavior
- explicit OpenAI hybrid mode control
- minimal deployment packaging

## Router And SQL Agent

New deterministic coverage includes:

- `Margin %` / `marge %` by country, category, or segment
- `ASP` / Average Selling Price by country, category, or segment
- revenue share by country
- yearly revenue evolution

The SQL Agent still validates generated SQL with the read-only SQL guard.

## RAG

The local knowledge base now documents:

- `Revenue Share %`
- `Year-over-Year Change`
- grouped `Margin %`
- grouped `Average Selling Price`
- clearer segment, country, and category usage

The retriever has extra synonym support for:

- sales / revenue
- share / contribution
- evolution / variation / growth
- margin rate / percentage

## Insight Agent

The Insight Agent now handles more SQL result shapes:

- `margin_pct`
- `average_selling_price`
- `revenue_share_pct`
- yearly KPI comparisons

It still avoids unsupported causal explanations.

## Visualization

The visualization builder now chooses:

- line charts for monthly or yearly evolution
- horizontal bars for top rankings
- standard bars for grouped comparisons

## Hybrid OpenAI Mode

OpenAI remains optional.

To avoid accidental cost, the LLM mode is controlled by:

```text
HYBRID_LLM_ENABLED=true
```

Without this flag, the project stays local even if an API key exists in `.env`.

## Packaging

Added:

- `Dockerfile`
- `.dockerignore`
- `docs/DEPLOYMENT.md`

Docker can be used for local demo packaging.
