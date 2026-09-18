"""Episode watched-state HTTP routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contracts import SetWatchedStateRequest
from app.application.use_cases import GetWatchedState, SetWatchedState
from app.database import get_db_session
from app.presentation.dependencies import get_user_id, get_watched_repository
from app.presentation.schemas import WatchedRequest, WatchedResponse

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.put("/{episode_id}/watched", response_model=WatchedResponse)
async def set_watched_state(
    episode_id: int,
    body: WatchedRequest,
    user_id=Depends(get_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> WatchedResponse:
    result = await SetWatchedState(get_watched_repository(session)).execute(
        SetWatchedStateRequest(user_id, episode_id, body.watched)
    )
    await session.commit()
    return WatchedResponse.model_validate(result, from_attributes=True)


@router.get("/{episode_id}/watched", response_model=WatchedResponse)
async def get_watched_state(
    episode_id: int,
    user_id=Depends(get_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> WatchedResponse:
    result = await GetWatchedState(get_watched_repository(session)).execute(user_id, episode_id)
    return WatchedResponse.model_validate(result, from_attributes=True)
