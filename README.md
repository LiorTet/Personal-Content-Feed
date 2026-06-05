# Personal-Content-Feed

A personal intelligent content feed engine built with FastAPI, LangGraph, and semantic agent memory.
This project combines web search, local LLM reasoning, vector embeddings, and a content archive to generate topical markdown research reports.

## 🚀 What this project does

- Accepts query topics through a POST `/scout` endpoint
- Runs a scout agent that performs web search and collects findings
- Generates embeddings for search snippets and archives them in PostgreSQL with `pgvector`
- Retrieves semantically relevant archived content
- Builds a markdown research report
- Saves final feed files to `feeds/`

## 🧠 Architecture

### Core modules
- `main.py`: FastAPI app, lifecycle, endpoints, and request logging
- `agent/graph.py`: Graph orchestration using `langgraph`
- `agent/memory_state.py`: Pydantic state models for graph input/output

### Agent nodes
- `agent/nodes/scout.py`: Runs the research scout and search tool
- `agent/nodes/archive.py`: Stores findings and embeddings in the archive
- `agent/nodes/retrieval.py`: Performs semantic retrieval and creates the report
- `agent/nodes/exporter.py`: Exports the final report to a markdown file

### Infrastructure
- `db/database.py`: Async PostgreSQL setup and DB initialization
- `core/logger_format.py`: Structured logging
- `core/timing.py`: Inference latency tracking

## 📦 Requirements

- Python 3.13+
- `uv` package manager
- PostgreSQL with the `vector` extension enabled
- `MISTRAL_API_KEY` environment variable
- `DATABASE_URL` environment variable

## ⚙️ Setup

1. Install dependencies:

```bash
uv sync
```

2. Configure environment variables:

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost:5432/content_feed"
export MISTRAL_API_KEY="your-mistral-api-key"
export OUTPUT_FEEDS_DIR="feeds"
```

3. Start the API:

```bash
uv run uvicorn main:app --reload
```

## 🧪 Testing

Run the test suite:

```bash
uv run pytest
```

## 🧪 CI / Quality checks

The repository includes a GitHub Actions workflow at `.github/workflows/ci.yml` that runs:
- `ruff` lint and format checks
- `mypy` type checking
- `pytest`
- a smoke test against `/health` and `/scout`

## 🧾 API usage

### Health checks

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/ready
curl http://127.0.0.1:8000/health/Agents
```

### Scout endpoint

```bash
curl -X POST http://127.0.0.1:8000/scout \
  -H "Content-Type: application/json" \
  -d '{
    "query": ["Latest articles and public interventions by Juan Manuel de Prada May 2026"],
    "findings": [],
    "iteration": 0,
    "critic_feedback": null,
    "final_report": null
  }'
```

## 📂 Output

- Generated feed files are written to `feeds/`
- Filenames include a timestamp and a sanitized query slug

## 🔧 Developer notes

- `call_api.py` is a helper script to call the `/scout` endpoint
- `agent/test.py` is a local graph debug harness
- `ENV=ci` disables DB initialization during CI runs
- The project uses `langgraph` for stateful agent orchestration and memory persistence

## 🌱 Recommended next steps

- Add docker-compose services for PostgreSQL and the API
- Improve request validation and query formatting
- Add retry handling for search and embedding failures
- Expand the test suite for graph behavior and DB persistence
