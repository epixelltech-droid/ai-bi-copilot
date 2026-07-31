# Business Test Protocol

This protocol helps validate the BI copilot with realistic business questions after each important update.

## Goal

Check three things:
- the route is correct (`sql` or `rag`)
- the answer is understandable for a business user
- the hybrid mode behaves as expected (`llm` when configured, local fallback otherwise)

## Before Testing

1. Start the API locally:
   `python -m uvicorn app.main:app --reload`
2. Confirm the health endpoint:
   `GET /health`
3. Decide which mode you are testing:
   - local fallback only: no `OPENAI_API_KEY`
   - hybrid mode: `OPENAI_API_KEY` configured
4. Use the same `user_id` for follow-up questions when you want memory to apply.

## Test Set A - Analytical Questions

Use these questions:
- `Quel est le chiffre d'affaires total ?`
- `Quel est le chiffre d'affaires par pays ?`
- `Quel est le chiffre d'affaires par mois ?`
- `Quelle est la marge par categorie ?`
- `Quels sont les 10 meilleurs clients ?`
- `Compare le chiffre d'affaires entre la France et le Maroc.`

Expected checks:
- route = `sql`
- query language = `SQL`
- rows are returned
- answer mentions the main business result
- visualization is enabled when the result shape fits a chart

## Test Set B - Documentary Questions

Use these questions:
- `Que signifie Revenue ?`
- `Comment calcule-t-on la marge ?`
- `Que veut dire SMB ?`
- `Qu'est-ce qu'un client Enterprise ?`
- `Comment est defini un top product ?`
- `Que signifie EBITDA ?`

Expected checks:
- route = `rag`
- query language = `NONE`
- sources are returned for known questions
- unknown questions stay safe and do not invent content

## Test Set C - Follow-up Questions

Use the same `user_id`:
- `Quel est le chiffre d'affaires par pays ?`
- `et en 2026 ?`
- `Quel est le chiffre d'affaires total ?`
- `et par mois ?`
- `Que signifie Revenue ?`
- `et la marge ?`

Expected checks:
- memory is used when the second question depends on the first
- `resolved_question` in history is more explicit than the raw follow-up
- `used_memory = true` appears in audit history

## Hybrid Audit Checks

Open:
`GET /api/history/{user_id}`

Check `hybrid_meta`:
- `llm.configured`
- `llm.provider`
- `llm.model`
- `router_mode`
- `router_reason`
- `rewritten_by_router`
- `sql_generation_mode` for SQL questions
- `response_mode`

## Pass Criteria

The release is acceptable if:
- core analytical questions route to SQL correctly
- core documentary questions route to RAG correctly
- no unsafe hallucination appears on unknown documentation questions
- follow-up memory still works
- hybrid audit fields are populated

## Suggested Regression Rhythm

- quick check after each prompt change: 6 questions
- full business check before Git push: all sets A, B, and C
- demo check before portfolio or client presentation: all sets plus UI walkthrough
