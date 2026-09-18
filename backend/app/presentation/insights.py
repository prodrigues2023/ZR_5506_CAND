"""AI insight HTTP routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contracts import GenerateInsightRequest
from app.application.insights import GenerateInsight
from app.database import get_db_session
from app.presentation.dependencies import (
    get_catalog,
    get_comment_repository,
    get_insight_generator,
    get_insight_repository,
)
from app.presentation.schemas import InsightResponse

router = APIRouter(tags=["insights"])


async def _generate(
    target_type: str,
    target_id: int,
    catalog,
    session: AsyncSession,
    generator,
) -> InsightResponse:
    result = await GenerateInsight(
        catalog,
        get_comment_repository(session),
        get_insight_repository(session),
        generator,
    ).execute(GenerateInsightRequest(target_type, target_id))
    await session.commit()
    return InsightResponse(insight=result.insight.text, used_fallback=result.insight.used_fallback)


@router.get("/series/{series_id}/insight", response_model=InsightResponse)
async def series_insight(
    series_id: int,
    catalog=Depends(get_catalog),
    session: AsyncSession = Depends(get_db_session),
    generator=Depends(get_insight_generator),
) -> InsightResponse:
    return await _generate("series", series_id, catalog, session, generator)


@router.get("/episodes/{episode_id}/insight", response_model=InsightResponse)
async def episode_insight(
    episode_id: int,
    catalog=Depends(get_catalog),
    session: AsyncSession = Depends(get_db_session),
    generator=Depends(get_insight_generator),
) -> InsightResponse:
    return await _generate("episode", episode_id, catalog, session, generator)
