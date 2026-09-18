"""HTTP request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SeriesResponse(BaseModel):
    id: int
    title: str
    year: int | None
    poster_url: str | None
    summary: str | None
    genres: tuple[str, ...]


class SearchResponse(BaseModel):
    results: tuple[SeriesResponse, ...]


class EpisodeResponse(BaseModel):
    id: int
    series_id: int
    season: int
    number: int
    title: str
    summary: str | None
    airdate: str | None
    poster_url: str | None
    watched: bool


class SeasonResponse(BaseModel):
    season: int
    episodes: tuple[EpisodeResponse, ...]


class SeriesDetailsResponse(BaseModel):
    series: SeriesResponse
    seasons: tuple[SeasonResponse, ...]
    watched_episode_ids: frozenset[int]
    comments: tuple["CommentResponse", ...]


class WatchedRequest(BaseModel):
    watched: bool


class WatchedResponse(BaseModel):
    episode_id: int
    watched: bool
    updated_at: datetime


class CommentRequest(BaseModel):
    series_id: int | None = None
    episode_id: int | None = None
    content: str = Field(min_length=1, max_length=2000)

    @model_validator(mode="after")
    def exactly_one_target(self) -> "CommentRequest":
        if (self.series_id is None) == (self.episode_id is None):
            raise ValueError("Exactly one of series_id or episode_id is required")
        return self


class CommentResponse(BaseModel):
    id: str
    author_id: str
    author_label: str
    target_type: Literal["series", "episode"]
    target_id: int
    content: str
    created_at: datetime


class InsightResponse(BaseModel):
    insight: str
    used_fallback: bool
