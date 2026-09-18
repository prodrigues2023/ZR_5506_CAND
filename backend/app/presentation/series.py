"""Series and search HTTP routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contracts import GetSeriesDetailsRequest, SearchSeriesRequest
from app.application.use_cases import GetSeriesDetails, SearchSeries
from app.database import get_db_session
from app.presentation.dependencies import (
    get_catalog,
    get_comment_repository,
    get_series_cache,
    get_user_id,
    get_watched_repository,
)
from app.presentation.identity import anonymous_label
from app.presentation.schemas import (
    CommentResponse,
    EpisodeResponse,
    SearchResponse,
    SeasonResponse,
    SeriesDetailsResponse,
    SeriesResponse,
)

router = APIRouter(prefix="/series", tags=["series"])


def _comment_response(comment) -> CommentResponse:
    target_type = "series" if comment.series_id is not None else "episode"
    target_id = comment.series_id if comment.series_id is not None else comment.episode_id
    return CommentResponse(
        id=str(comment.id),
        author_id=str(comment.author_id),
        author_label=anonymous_label(comment.author_id),
        target_type=target_type,
        target_id=target_id,
        content=comment.content,
        created_at=comment.created_at,
    )


@router.get("/search", response_model=SearchResponse)
async def search_series(
    q: str = Query(min_length=1, max_length=200),
    catalog=Depends(get_catalog),
) -> SearchResponse:
    result = await SearchSeries(catalog).execute(SearchSeriesRequest(q))
    return SearchResponse(
        results=tuple(
            SeriesResponse.model_validate(item, from_attributes=True) for item in result.results
        )
    )


@router.get("/{series_id}", response_model=SeriesDetailsResponse)
async def get_series_details(
    series_id: int,
    user_id=Depends(get_user_id),
    catalog=Depends(get_catalog),
    session: AsyncSession = Depends(get_db_session),
) -> SeriesDetailsResponse:
    result = await GetSeriesDetails(
        catalog,
        get_series_cache(session),
        get_watched_repository(session),
        get_comment_repository(session),
    ).execute(GetSeriesDetailsRequest(series_id, user_id))
    await session.commit()
    seasons = tuple(
        SeasonResponse(
            season=season.season,
            episodes=tuple(
                EpisodeResponse(
                    id=episode.id,
                    series_id=episode.series_id,
                    season=episode.season,
                    number=episode.number,
                    title=episode.title,
                    summary=episode.summary,
                    airdate=episode.airdate,
                    poster_url=episode.poster_url,
                    watched=episode.id in result.watched_episode_ids,
                )
                for episode in season.episodes
            ),
        )
        for season in result.seasons
    )
    return SeriesDetailsResponse(
        series=SeriesResponse.model_validate(result.series, from_attributes=True),
        seasons=seasons,
        watched_episode_ids=result.watched_episode_ids,
        comments=tuple(_comment_response(comment) for comment in result.comments),
    )
