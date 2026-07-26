# AI BI Copilot - Local Multi-Agent Analytics

Projet local de Copilot BI pour poser des questions en langage naturel sur un jeu de donnees SQLite.

Cette V1 est concue pour rester :

- locale
- simple
- testable
- lisible pour un debutant

Elle fonctionne aujourd'hui avec :

- FastAPI
- LangGraph
- SQLite
- RAG local sur fichiers Markdown
- generation SQL deterministe
- reponses metier deterministes

## Vision

Le projet a deux objectifs simples :

1. repondre aux questions analytiques sur les donnees
2. repondre aux questions documentaires sur les KPI et regles metier

Exemples :

- `Quel est le chiffre d'affaires par pays ?`
- `Comment calcule-t-on la marge ?`

## Architecture rapide

```text
POST /api/chat
  -> FastAPI
  -> LangGraph
  -> Router
     -> SQL Agent -> SQLite -> Insight Agent
     -> RAG local -> knowledge_base
  -> JSON response
```

## Fonctionnalites
- question en langage naturel
- routage SQL / Power BI / RAG
- generation SQL
- generation DAX
- execution SQL locale avec SQLite
- RAG local de regles metier
- analyse automatique
- guardrails SQL
- audit trail
- API FastAPI
- orchestration LangGraph

## Etat actuel

Le projet fournit aujourd'hui :

- une route SQL pour les questions analytiques
- une route RAG pour les questions documentaires
- un modele BI en etoile dans SQLite
- un audit simple
- une suite de tests locale

## Structure principale

```text
app/
  agents/
  api/
  connectors/
  core/
  models/
  rag/
  tools/
knowledge_base/
scripts/
tests/
docs/
```

## Prerequis
- Windows
- Python 3.11 recommande

## Demarrage sous Windows

### CMD

```cmd
cd C:\Users\Workspace\Documents\ai-bi-copilot-starter\ai-bi-copilot
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
python scripts\init_demo_db.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### PowerShell

```powershell
Set-Location C:\Users\Workspace\Documents\ai-bi-copilot-starter\ai-bi-copilot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python scripts/init_demo_db.py
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Si l'activation du venv pose probleme, utilise directement le Python du projet :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/init_demo_db.py
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Ouvrir ensuite `http://127.0.0.1:8000/docs`.

Verifier rapidement que l'API repond :

```powershell
Invoke-WebRequest http://127.0.0.1:8000/health
```

Exemple de payload pour `POST /api/chat` :

```json
{
  "question": "Quel est le chiffre d'affaires par pays ?",
  "user_id": "anas",
  "source": "auto"
}
```

## Mode local

La V1 locale fonctionne sans Azure OpenAI, sans SQL Server et sans Power BI configure.
Dans ce cas, le projet utilise des reponses deterministes pour le SQL, le DAX et le resume metier.

## Variables optionnelles

Le fichier `.env.example` se concentre sur la V1 locale et laisse seulement les options encore supportees par le code actuel.

## Suite

Voir `docs/ROADMAP.md` et `docs/DEMO_SCRIPT.md`.

## Documentation

Documentation projet :

- `docs/PROJECT_OVERVIEW.md`
- `docs/ARCHITECTURE.md`
- `docs/TECHNICAL_DOCUMENTATION.md`
- `docs/DOCUMENTATION_WORKFLOW.md`
- `CHANGELOG.md`

Regle simple du projet :

- a chaque changement important du code, on met a jour la documentation concernee dans le meme cycle de travail
