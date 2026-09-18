from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain.entities import Comment


def test_comment_requires_exactly_one_target() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        Comment(
            id=uuid4(),
            author_id=uuid4(),
            content="A comment",
            created_at=datetime.now(UTC),
        )


def test_comment_accepts_series_target() -> None:
    comment = Comment(
        id=uuid4(),
        author_id=uuid4(),
        content="A comment",
        created_at=datetime.now(UTC),
        series_id=139,
    )

    assert comment.series_id == 139
    assert comment.episode_id is None
