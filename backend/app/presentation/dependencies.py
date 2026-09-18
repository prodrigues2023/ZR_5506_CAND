"""FastAPI dependency providers and browser identity handling."""

from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db_session
from app.infrastructure.ai import HuggingFaceInsightGenerator
from app.infrastructure.repositories import (
    SQLCommentRepository,
    SQLInsightRepository,
    SQLSeriesCache,
    SQLWatchedEpisodeRepository,
)
from app.infrastructure.tvmaze import TVMazeClient


async def get_catalog() -> AsyncIterator[TVMazeClient]:
    settings = get_settings()
    client = TVMazeClient(settings)
    try:
        yield client
    finally:
        await client.aclose()


def get_user_id(request: Request, response: Response) -> UUID:
    settings: Settings = get_settings()
    raw_user_id = request.cookies.get(settings.anonymous_user_cookie)
    try:
        user_id = UUID(raw_user_id) if raw_user_id else uuid4()
    except ValueError:
        user_id = uuid4()
    if raw_user_id != str(user_id):
        response.set_cookie(
            key=settings.anonymous_user_cookie,
            value=str(user_id),
            httponly=True,
            samesite="lax",
            secure=settings.environment == "production",
            max_age=60 * 60 * 24 * 365,
        )
    return user_id


def get_watched_repository(session: AsyncSession = get_db_session) -> SQLWatchedEpisodeRepository:
    return SQLWatchedEpisodeRepository(session)


def get_series_cache(session: AsyncSession = get_db_session) -> SQLSeriesCache:
    return SQLSeriesCache(session)


def get_comment_repository(session: AsyncSession = get_db_session) -> SQLCommentRepository:
    return SQLCommentRepository(session)


async def get_insight_generator() -> AsyncIterator[HuggingFaceInsightGenerator]:
    generator = HuggingFaceInsightGenerator(get_settings())
    try:
        yield generator
    finally:
        await generator.aclose()


def get_insight_repository(session: AsyncSession = get_db_session) -> SQLInsightRepository:
    return SQLInsightRepository(session)
