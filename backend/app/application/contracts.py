"""Input and output contracts for application use cases."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.entities import Comment, Insight, SeasonEpisodes, Series


@dataclass(frozen=True, slots=True)
class SearchSeriesRequest:
    query: str


@dataclass(frozen=True, slots=True)
class SearchSeriesResponse:
    results: tuple[Series, ...]


@dataclass(frozen=True, slots=True)
class GetSeriesDetailsRequest:
    series_id: int
    user_id: UUID


@dataclass(frozen=True, slots=True)
class GetSeriesDetailsResponse:
    series: Series
    seasons: tuple[SeasonEpisodes, ...]
    watched_episode_ids: frozenset[int]
    comments: tuple[Comment, ...]


@dataclass(frozen=True, slots=True)
class SetWatchedStateRequest:
    user_id: UUID
    episode_id: int
    watched: bool


@dataclass(frozen=True, slots=True)
class AddCommentRequest:
    user_id: UUID
    content: str
    series_id: int | None = None
    episode_id: int | None = None


@dataclass(frozen=True, slots=True)
class GenerateInsightRequest:
    target_type: str
    target_id: int
    include_comments: bool = True


@dataclass(frozen=True, slots=True)
class InsightResponse:
    insight: Insight


@dataclass(frozen=True, slots=True)
class WatchedStateResponse:
    episode_id: int
    watched: bool
    updated_at: datetime
