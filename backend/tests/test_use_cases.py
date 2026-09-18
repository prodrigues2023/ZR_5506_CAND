from datetime import UTC, datetime
from uuid import uuid4

from app.application.contracts import GetSeriesDetailsRequest, SetWatchedStateRequest
from app.application.use_cases import GetSeriesDetails, GetWatchedState, SetWatchedState
from app.domain.entities import Episode, Series, WatchedEpisode


class FakeCatalog:
    def __init__(self) -> None:
        self.series_calls = 0
        self.episode_calls = 0
        self.series = Series(1, "Demo", 2020, None, "Summary", ("Drama",))
        self.episodes = (Episode(10, 1, 1, 1, "Pilot", "Episode", "2020-01-01", None),)

    async def get_series(self, series_id: int) -> Series:
        self.series_calls += 1
        return self.series

    async def get_episodes(self, series_id: int):
        self.episode_calls += 1
        return self.episodes


class FakeCache:
    def __init__(self) -> None:
        self.series = None
        self.episodes = None
        self.series_saves = 0
        self.episode_saves = 0

    async def get_series(self, series_id: int, *, now):
        return self.series

    async def save_series(self, series, *, raw_payload):
        self.series = series
        self.series_saves += 1

    async def get_episodes(self, series_id: int, *, now):
        return self.episodes

    async def save_episodes(self, episodes, *, raw_payloads):
        self.episodes = tuple(episodes)
        self.episode_saves += 1


class FakeWatched:
    async def list_for_series(self, user_id, series_id):
        return (WatchedEpisode(user_id, 10, True, datetime.now(UTC)),)

    async def get(self, user_id, episode_id):
        return None

    async def save(self, state):
        return state


class FakeComments:
    async def list_for_series(self, series_id):
        return ()


async def test_details_use_case_reads_and_writes_json_cache() -> None:
    catalog = FakeCatalog()
    cache = FakeCache()
    user_id = uuid4()
    use_case = GetSeriesDetails(catalog, cache, FakeWatched(), FakeComments())

    first = await use_case.execute(GetSeriesDetailsRequest(1, user_id))
    second = await use_case.execute(GetSeriesDetailsRequest(1, user_id))

    assert first.seasons[0].episodes[0].id == 10
    assert second.series.title == "Demo"
    assert catalog.series_calls == 1
    assert catalog.episode_calls == 1
    assert cache.series_saves == 1
    assert cache.episode_saves == 1


async def test_missing_watched_state_defaults_to_unwatched() -> None:
    result = await GetWatchedState(FakeWatched()).execute(uuid4(), 10)

    assert result.episode_id == 10
    assert result.watched is False


async def test_set_watched_state_uses_repository() -> None:
    result = await SetWatchedState(FakeWatched()).execute(SetWatchedStateRequest(uuid4(), 10, True))

    assert result.episode_id == 10
    assert result.watched is True
