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
2. Set `SERIES_HUGGINGFACE_API_KEY` in `.env`. This key is required for communication with the Hugging Face provider. Without it, the application starts and the other features remain available, but AI insight requests use only the deterministic fallback and do not call the external AI provider.
3. Start the complete stack:

**Bash:**

```bash
docker compose build --no-cache && docker compose up -d
```

**Command Prompt:**

```cmd
docker compose build --no-cache && docker compose up -d
```

**PowerShell:**

```powershell
docker compose build --no-cache; if ($LASTEXITCODE -eq 0) { docker compose up -d }
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
docker compose build --no-cache && docker compose up -d && curl --fail http://localhost:7777/api/health
```

The Hugging Face token should be injected by Jenkins credentials as `SERIES_HUGGINGFACE_API_KEY`; it must not be committed to the repository.
