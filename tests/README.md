# Tests

The backend test suite covers domain entities, application use cases, TVMaze mapping,
AI provider success and fallback behavior, health checks, and anonymous identity.

Run the backend checks with:

```bash
cd backend
uv run ruff check app migrations tests
uv run pytest
```
