"""SQLAlchemy implementations of application persistence ports."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Comment, Episode, Insight, Series, WatchedEpisode
from app.infrastructure.models import (
    CommentModel,
    EpisodeCacheModel,
    InsightModel,
    SeriesCacheModel,
    WatchedEpisodeModel,
)


def _to_series(model: SeriesCacheModel) -> Series:
    return Series(
        model.id, model.title, model.year, model.poster_url, model.summary, tuple(model.genres)
    )


def _to_episode(model: EpisodeCacheModel) -> Episode:
    return Episode(
        model.id,
        model.series_id,
        model.season,
        model.number,
        model.title,
        model.summary,
        model.airdate,
        model.poster_url,
    )


class SQLSeriesCache:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_series(self, series_id: int, *, now: datetime) -> Series | None:
        model = await self.session.get(SeriesCacheModel, series_id)
        return _to_series(model) if model else None

    async def save_series(self, series: Series, *, raw_payload: dict) -> None:
        model = await self.session.get(SeriesCacheModel, series.id)
        if model is None:
            model = SeriesCacheModel(id=series.id)
            self.session.add(model)
        model.title = series.title
        model.year = series.year
        model.poster_url = series.poster_url
        model.summary = series.summary
        model.genres = list(series.genres)
        model.raw_payload = raw_payload
        model.fetched_at = datetime.utcnow()

    async def get_episodes(self, series_id: int, *, now: datetime) -> Sequence[Episode] | None:
        result = await self.session.scalars(
            select(EpisodeCacheModel)
            .where(EpisodeCacheModel.series_id == series_id)
            .order_by(EpisodeCacheModel.season, EpisodeCacheModel.number)
        )
        episodes = tuple(result.all())
        return tuple(_to_episode(item) for item in episodes) or None

    async def save_episodes(
        self, episodes: Sequence[Episode], *, raw_payloads: Sequence[dict]
    ) -> None:
        for episode, payload in zip(episodes, raw_payloads, strict=True):
            model = await self.session.get(EpisodeCacheModel, episode.id)
            if model is None:
                model = EpisodeCacheModel(id=episode.id)
                self.session.add(model)
            model.series_id = episode.series_id
            model.season = episode.season
            model.number = episode.number
            model.title = episode.title
            model.summary = episode.summary
            model.airdate = episode.airdate
            model.poster_url = episode.poster_url
            model.raw_payload = payload
            model.fetched_at = datetime.utcnow()


class SQLWatchedEpisodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: UUID, episode_id: int) -> WatchedEpisode | None:
        model = await self.session.scalar(
            select(WatchedEpisodeModel).where(
                WatchedEpisodeModel.user_id == user_id,
                WatchedEpisodeModel.episode_id == episode_id,
            )
        )
        return self._to_entity(model) if model else None

    async def list_for_series(self, user_id: UUID, series_id: int) -> Sequence[WatchedEpisode]:
        result = await self.session.scalars(
            select(WatchedEpisodeModel)
            .join(EpisodeCacheModel, EpisodeCacheModel.id == WatchedEpisodeModel.episode_id)
            .where(
                WatchedEpisodeModel.user_id == user_id,
                EpisodeCacheModel.series_id == series_id,
            )
        )
        return tuple(self._to_entity(model) for model in result.all())

    async def save(self, state: WatchedEpisode) -> WatchedEpisode:
        model = await self.session.scalar(
            select(WatchedEpisodeModel).where(
                WatchedEpisodeModel.user_id == state.user_id,
                WatchedEpisodeModel.episode_id == state.episode_id,
            )
        )
        if model is None:
            model = WatchedEpisodeModel(user_id=state.user_id, episode_id=state.episode_id)
            self.session.add(model)
        model.watched = state.watched
        model.updated_at = state.updated_at
        await self.session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: WatchedEpisodeModel) -> WatchedEpisode:
        return WatchedEpisode(model.user_id, model.episode_id, model.watched, model.updated_at)


class SQLCommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_series(self, series_id: int) -> Sequence[Comment]:
        result = await self.session.scalars(
            select(CommentModel)
            .where(CommentModel.series_id == series_id)
            .order_by(CommentModel.created_at)
        )
        return tuple(self._to_entity(model) for model in result.all())

    async def list_for_episode(self, episode_id: int) -> Sequence[Comment]:
        result = await self.session.scalars(
            select(CommentModel)
            .where(CommentModel.episode_id == episode_id)
            .order_by(CommentModel.created_at)
        )
        return tuple(self._to_entity(model) for model in result.all())

    async def add(self, comment: Comment) -> Comment:
        model = CommentModel(
            id=comment.id,
            author_id=comment.author_id,
            series_id=comment.series_id,
            episode_id=comment.episode_id,
            content=comment.content,
            created_at=comment.created_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: CommentModel) -> Comment:
        return Comment(
            model.id,
            model.author_id,
            model.content,
            model.created_at,
            model.series_id,
            model.episode_id,
        )


class SQLInsightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, target_type: str, target_id: int) -> Insight | None:
        model = await self.session.scalar(
            select(InsightModel).where(
                InsightModel.target_type == target_type,
                InsightModel.target_id == target_id,
            )
        )
        return self._to_entity(model) if model else None

    async def save(self, insight: Insight) -> Insight:
        model = await self.session.scalar(
            select(InsightModel).where(
                InsightModel.target_type == insight.target_type,
                InsightModel.target_id == insight.target_id,
            )
        )
        if model is None:
            model = InsightModel(target_type=insight.target_type, target_id=insight.target_id)
            self.session.add(model)
        model.text = insight.text
        model.used_fallback = insight.used_fallback
        model.generated_at = insight.generated_at
        await self.session.flush()
        return self._to_entity(model)

    @staticmethod
    def _to_entity(model: InsightModel) -> Insight:
        return Insight(
            model.target_type, model.target_id, model.text, model.used_fallback, model.generated_at
        )
