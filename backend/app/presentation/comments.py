"""Comment HTTP routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.contracts import AddCommentRequest
from app.application.use_cases import AddComment, ListComments
from app.database import get_db_session
from app.presentation.dependencies import get_comment_repository, get_user_id
from app.presentation.identity import anonymous_label
from app.presentation.schemas import CommentRequest, CommentResponse

router = APIRouter(prefix="/comments", tags=["comments"])


def _response(comment) -> CommentResponse:
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


@router.get("", response_model=tuple[CommentResponse, ...])
async def list_comments(
    series_id: int | None = Query(default=None),
    episode_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_db_session),
) -> tuple[CommentResponse, ...]:
    if (series_id is None) == (episode_id is None):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Provide exactly one target")
    use_case = ListComments(get_comment_repository(session))
    comments = (
        await use_case.for_series(series_id)
        if series_id is not None
        else await use_case.for_episode(episode_id)
    )
    return tuple(_response(comment) for comment in comments)


@router.post("", response_model=CommentResponse, status_code=201)
async def add_comment(
    body: CommentRequest,
    user_id=Depends(get_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> CommentResponse:
    comment = await AddComment(get_comment_repository(session)).execute(
        AddCommentRequest(user_id, body.content, body.series_id, body.episode_id)
    )
    await session.commit()
    return _response(comment)
