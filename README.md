# Interactive TV Series Experience

Interactive TV series experience built for the Software Architect technical challenge.

## Project structure

- `backend/` - FastAPI service
- `frontend/` - React + Vite application
- `tests/` - automated tests
- `infra/` - container and web-server configuration
- `docs/` - architecture and presentation materials

## Run with Docker

Prerequisites: Docker Engine with Compose support.

1. Copy `.env.example` to `.env`.
2. Set `SERIES_DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` in `.env`.
3. Add `SERIES_HUGGINGFACE_API_KEY` if AI provider calls should be enabled. The application still works with the deterministic fallback when the key is empty.
3. Start the complete stack:

```bash
docker compose up --build
```

Open <http://localhost:7777>. The application container serves the React build through Nginx, proxies `/api` to FastAPI, and runs migrations automatically. PostgreSQL 18 stores relational user state and TVMaze JSONB snapshots.

## Local development

Backend:

```bash
cd backend
uv sync --dev
uv run pytest
uv run uvicorn app.main:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Quality checks

```bash
cd backend && uv run ruff check app migrations && uv run pytest
cd frontend && npm run build
```

## Jenkins

The pipeline can use the same single-command deployment check:

```bash
docker compose up --build -d
curl --fail http://localhost:7777/api/health
```

The Hugging Face token should be injected by Jenkins credentials as `SERIES_HUGGINGFACE_API_KEY`; it must not be committed to the repository.
