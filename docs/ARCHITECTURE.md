# Architecture

## High-Level View

The project follows a simple local multi-agent architecture:

1. the API receives a user question
2. the Router chooses the right path
3. the selected agent produces an answer
4. the audit layer stores the interaction

## Main Flow

```text
User
  -> FastAPI (`POST /api/chat`)
    -> LangGraph
      -> Router
        -> SQL Agent
          -> SQL Guard
          -> SQLite
          -> Insight Agent
        -> RAG Agent
          -> Document Loader
          -> Retriever
          -> Answer Builder
        -> Power BI / DAX path (available but not required for local V1)
    -> API response
    -> Audit log
```

## Main Components

### 1. API

Files:

- `app/main.py`
- `app/api/routes.py`

Role:

- expose the HTTP interface
- receive the question
- return the final structured response

### 2. LangGraph Orchestration

File:

- `app/agents/graph.py`

Role:

- connect the Router to the SQL and RAG paths
- keep a shared state during request execution

### 3. Router

File:

- `app/agents/router.py`

Role:

- decide whether the question is:
  - analytical
  - documentary
  - Power BI / DAX related

The current router is deterministic and based on normalized keywords and phrases.

### 4. SQL Path

Files:

- `app/agents/sql_agent.py`
- `app/tools/sql_guard.py`
- `app/connectors/sqlite_demo.py`
- `app/agents/insight_agent.py`

Role:

- generate read-only SQL
- validate it
- execute it on SQLite
- convert rows into a business answer

### 5. RAG Path

Files:

- `app/rag/document_loader.py`
- `app/rag/retriever.py`
- `app/rag/knowledge.py`

Role:

- read the local Markdown knowledge base
- retrieve relevant chunks
- build a grounded answer without using a cloud LLM

### 6. Metadata Layer

File:

- `app/connectors/schema_metadata.py`

Role:

- inspect SQLite dynamically
- expose tables, columns, primary keys, foreign keys, and relations
- help the SQL Agent understand the official schema

### 7. Data Layer

Files:

- `scripts/init_demo_db.py`
- `data/demo.db`

Role:

- create and store the local BI demo dataset

Official BI model:

- `fact_sales`
- `dim_customer`
- `dim_product`
- `dim_date`

### 8. Knowledge Base

Folder:

- `knowledge_base/`

Main documents:

- `kpi_dictionary.md`
- `data_dictionary.md`
- `business_rules.md`

Role:

- store business definitions and documentation used by the local RAG

### 9. Audit

File:

- `app/core/audit.py`

Role:

- persist a trace of what happened for each request

## Response Types

### SQL response

Typical output contains:

- `route = "sql"`
- `answer`
- `artifact.language = "SQL"`
- generated query
- returned rows
- `sources = []`

### RAG response

Typical output contains:

- `route = "rag"`
- `answer`
- `artifact.language = "NONE"`
- no SQL query
- no tabular data
- `sources = [...]`

## Design Choices

The V1 intentionally favors:

- local execution
- deterministic behavior
- simple readable code
- no Internet dependency
- beginner-friendly architecture

This makes the project easier to understand, test, and extend.
