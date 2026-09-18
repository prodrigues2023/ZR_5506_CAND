"""Framework-independent domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Series:
    """A TV series snapshot relevant to the application."""

    id: int
    title: str
    year: int | None
    poster_url: str | None
    summary: str | None
    genres: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Episode:
    """An episode belonging to a series."""

    id: int
    series_id: int
    season: int
    number: int
    title: str
    summary: str | None
    airdate: str | None
    poster_url: str | None


@dataclass(frozen=True, slots=True)
class UserIdentity:
    """Anonymous browser identity used for user-scoped state."""

    id: UUID


@dataclass(frozen=True, slots=True)
class Comment:
    """An append-only comment attached to one target."""

    id: UUID
    author_id: UUID
    content: str
    created_at: datetime
    series_id: int | None = None
    episode_id: int | None = None

    def __post_init__(self) -> None:
        if (self.series_id is None) == (self.episode_id is None):
            raise ValueError("A comment must target exactly one series or episode")


@dataclass(frozen=True, slots=True)
class WatchedEpisode:
    """A user's watched state for an episode."""

    user_id: UUID
    episode_id: int
    watched: bool
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class Insight:
    """Generated text and provenance for an insight."""

    target_type: str
    target_id: int
    text: str
    used_fallback: bool
    generated_at: datetime


@dataclass(frozen=True, slots=True)
class SeasonEpisodes:
    """Episodes grouped under one season for presentation."""

    season: int
    episodes: tuple[Episode, ...] = field(default_factory=tuple)
