"""Ports consumed by application use cases."""

from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from app.domain.entities import Comment, Episode, Insight, Series, WatchedEpisode


class SeriesCatalog(Protocol):
    """Read series data from a catalog provider such as TVMaze."""

    async def search(self, query: str) -> Sequence[Series]: ...

    async def get_series(self, series_id: int) -> Series: ...

    async def get_episodes(self, series_id: int) -> Sequence[Episode]: ...

    async def get_episode(self, episode_id: int) -> Episode: ...


class SeriesCache(Protocol):
    """Store and retrieve external series snapshots."""

    async def get_series(self, series_id: int, *, now: datetime) -> Series | None: ...

    async def save_series(self, series: Series, *, raw_payload: dict) -> None: ...

    async def get_episodes(self, series_id: int, *, now: datetime) -> Sequence[Episode] | None: ...

    async def save_episodes(
        self, episodes: Sequence[Episode], *, raw_payloads: Sequence[dict]
    ) -> None: ...


class WatchedEpisodeRepository(Protocol):
    """Persist browser-scoped watched state."""

    async def get(self, user_id: UUID, episode_id: int) -> WatchedEpisode | None: ...

    async def list_for_series(self, user_id: UUID, series_id: int) -> Sequence[WatchedEpisode]: ...

    async def save(self, state: WatchedEpisode) -> WatchedEpisode: ...


class CommentRepository(Protocol):
    """Persist and query append-only comments."""

    async def list_for_series(self, series_id: int) -> Sequence[Comment]: ...

    async def list_for_episode(self, episode_id: int) -> Sequence[Comment]: ...

    async def add(self, comment: Comment) -> Comment: ...


class InsightGenerator(Protocol):
    """Generate an insight independently of the selected AI provider."""

    async def generate(
        self,
        *,
        target_type: str,
        target_id: int,
        title: str,
        summary: str | None,
        genres: Sequence[str],
        comments: Sequence[str],
    ) -> Insight: ...


class InsightRepository(Protocol):
    """Cache generated insights."""

    async def get(self, target_type: str, target_id: int) -> Insight | None: ...

    async def save(self, insight: Insight) -> Insight: ...
