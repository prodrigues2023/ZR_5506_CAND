"""Application use cases coordinating domain ports."""

from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.application.contracts import (
    AddCommentRequest,
    GetSeriesDetailsRequest,
    GetSeriesDetailsResponse,
    SearchSeriesRequest,
    SearchSeriesResponse,
    SetWatchedStateRequest,
    WatchedStateResponse,
)
from app.application.exceptions import InvalidRequest
from app.application.ports import (
    CommentRepository,
    SeriesCache,
    SeriesCatalog,
    WatchedEpisodeRepository,
)
from app.domain.entities import Comment, SeasonEpisodes, WatchedEpisode


class SearchSeries:
    def __init__(self, catalog: SeriesCatalog) -> None:
        self.catalog = catalog

    async def execute(self, request: SearchSeriesRequest) -> SearchSeriesResponse:
        query = request.query.strip()
        if not query:
            raise InvalidRequest("Search query cannot be empty")
        return SearchSeriesResponse(results=tuple(await self.catalog.search(query)))


class GetSeriesDetails:
    def __init__(
        self,
        catalog: SeriesCatalog,
        cache: SeriesCache,
        watched_repository: WatchedEpisodeRepository,
        comment_repository: CommentRepository,
    ) -> None:
        self.catalog = catalog
        self.cache = cache
        self.watched_repository = watched_repository
        self.comment_repository = comment_repository

    async def execute(self, request: GetSeriesDetailsRequest) -> GetSeriesDetailsResponse:
        now = datetime.now(UTC)
        series = await self.cache.get_series(request.series_id, now=now)
        episodes = await self.cache.get_episodes(request.series_id, now=now)
        if series is None:
            series = await self.catalog.get_series(request.series_id)
            await self.cache.save_series(series, raw_payload=self._series_payload(series))
        if episodes is None:
            episodes = tuple(await self.catalog.get_episodes(request.series_id))
            await self.cache.save_episodes(
                episodes,
                raw_payloads=tuple(self._episode_payload(episode) for episode in episodes),
            )
        episodes = tuple(episodes)
        watched = await self.watched_repository.list_for_series(request.user_id, request.series_id)
        comments = await self.comment_repository.list_for_series(request.series_id)
        watched_ids = frozenset(item.episode_id for item in watched if item.watched)
        seasons = self._group_by_season(episodes)
        return GetSeriesDetailsResponse(series, seasons, watched_ids, tuple(comments))

    @staticmethod
    def _group_by_season(episodes: Sequence) -> tuple[SeasonEpisodes, ...]:
        grouped: dict[int, list] = {}
        for episode in episodes:
            grouped.setdefault(episode.season, []).append(episode)
        return tuple(SeasonEpisodes(season, tuple(grouped[season])) for season in sorted(grouped))

    @staticmethod
    def _series_payload(series) -> dict:
        return {
            "id": series.id,
            "name": series.title,
            "premiered": f"{series.year}-01-01" if series.year else None,
            "genres": list(series.genres),
            "summary": series.summary,
            "image": {"original": series.poster_url} if series.poster_url else None,
        }

    @staticmethod
    def _episode_payload(episode) -> dict:
        return {
            "id": episode.id,
            "season": episode.season,
            "number": episode.number,
            "name": episode.title,
            "summary": episode.summary,
            "airdate": episode.airdate,
            "image": {"original": episode.poster_url} if episode.poster_url else None,
        }


class SetWatchedState:
    def __init__(self, repository: WatchedEpisodeRepository) -> None:
        self.repository = repository

    async def execute(self, request: SetWatchedStateRequest) -> WatchedStateResponse:
        state = WatchedEpisode(
            user_id=request.user_id,
            episode_id=request.episode_id,
            watched=request.watched,
            updated_at=datetime.now(UTC),
        )
        saved = await self.repository.save(state)
        return WatchedStateResponse(saved.episode_id, saved.watched, saved.updated_at)


class GetWatchedState:
    def __init__(self, repository: WatchedEpisodeRepository) -> None:
        self.repository = repository

    async def execute(self, user_id: UUID, episode_id: int) -> WatchedStateResponse:
        state = await self.repository.get(user_id, episode_id)
        if state is None:
            return WatchedStateResponse(episode_id, False, datetime.now(UTC))
        return WatchedStateResponse(state.episode_id, state.watched, state.updated_at)


class ListComments:
    def __init__(self, repository: CommentRepository) -> None:
        self.repository = repository

    async def for_series(self, series_id: int) -> tuple[Comment, ...]:
        return tuple(await self.repository.list_for_series(series_id))

    async def for_episode(self, episode_id: int) -> tuple[Comment, ...]:
        return tuple(await self.repository.list_for_episode(episode_id))


class AddComment:
    def __init__(self, repository: CommentRepository) -> None:
        self.repository = repository

    async def execute(self, request: AddCommentRequest) -> Comment:
        content = request.content.strip()
        if not content:
            raise InvalidRequest("Comment content cannot be empty")
        if len(content) > 2000:
            raise InvalidRequest("Comment content cannot exceed 2000 characters")
        comment = Comment(
            id=uuid4(),
            author_id=request.user_id,
            content=content,
            created_at=datetime.now(UTC),
            series_id=request.series_id,
            episode_id=request.episode_id,
        )
        return await self.repository.add(comment)
