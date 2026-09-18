"""Health endpoint for orchestration and pipeline checks."""

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Return a lightweight application liveness response."""

    return {"status": "ok"}
