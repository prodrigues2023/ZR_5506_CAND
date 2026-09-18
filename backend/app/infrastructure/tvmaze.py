"""TVMaze HTTP adapter."""

import re
from collections.abc import Sequence

import httpx

from app.application.exceptions import ResourceNotFound
from app.config import Settings
from app.domain.entities import Episode, Series


def _clean_summary(summary: str | None) -> str | None:
    if not summary:
        return None
    return re.sub(r"<[^>]+>", "", summary).strip()


def _year(premiered: str | None) -> int | None:
    return int(premiered[:4]) if premiered and premiered[:4].isdigit() else None


def _series_from_payload(payload: dict) -> Series:
    image = payload.get("image") or {}
    return Series(
        id=int(payload["id"]),
        title=payload.get("name", "Untitled"),
        year=_year(payload.get("premiered")),
        poster_url=image.get("original") or image.get("medium"),
        summary=_clean_summary(payload.get("summary")),
        genres=tuple(payload.get("genres") or ()),
    )


def _episode_from_payload(payload: dict, series_id: int) -> Episode:
    image = payload.get("image") or {}
    return Episode(
        id=int(payload["id"]),
        series_id=series_id,
        season=int(payload.get("season") or 0),
        number=int(payload.get("number") or 0),
        title=payload.get("name", "Untitled"),
        summary=_clean_summary(payload.get("summary")),
        airdate=payload.get("airdate"),
        poster_url=image.get("original") or image.get("medium"),
    )


class TVMazeClient:
    """Async implementation of the series catalog port."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            base_url=str(settings.tvmaze_base_url).rstrip("/")
        )
        self._owns_client = client is None

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def search(self, query: str) -> Sequence[Series]:
        response = await self._client.get("/search/shows", params={"q": query})
        response.raise_for_status()
        return tuple(_series_from_payload(item["show"]) for item in response.json())

    async def get_series(self, series_id: int) -> Series:
        response = await self._client.get(f"/shows/{series_id}")
        if response.status_code == 404:
            raise ResourceNotFound(f"Series {series_id} was not found")
        response.raise_for_status()
        return _series_from_payload(response.json())

    async def get_episodes(self, series_id: int) -> Sequence[Episode]:
        response = await self._client.get(f"/shows/{series_id}/episodes")
        if response.status_code == 404:
            raise ResourceNotFound(f"Series {series_id} was not found")
        response.raise_for_status()
        return tuple(_episode_from_payload(item, series_id) for item in response.json())

    async def get_episode(self, episode_id: int) -> Episode:
        response = await self._client.get(f"/episodes/{episode_id}", params={"embed": "show"})
        if response.status_code == 404:
            raise ResourceNotFound(f"Episode {episode_id} was not found")
        response.raise_for_status()
        payload = response.json()
        series_id = int((payload.get("_embedded") or {}).get("show", {}).get("id") or 0)
        if not series_id:
            raise ResourceNotFound(f"Parent series for episode {episode_id} was not found")
        return _episode_from_payload(payload, series_id)
