"""Create initial persistence schema."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    uuid = postgresql.UUID(as_uuid=True)
    jsonb = postgresql.JSONB(astext_type=sa.Text())
    op.create_table(
        "users",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "series_cache",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("year", sa.Integer),
        sa.Column("poster_url", sa.String(2000)),
        sa.Column("summary", sa.Text),
        sa.Column("genres", jsonb, nullable=False),
        sa.Column("raw_payload", jsonb, nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "episode_cache",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("series_id", sa.Integer, nullable=False),
        sa.Column("season", sa.Integer, nullable=False),
        sa.Column("number", sa.Integer, nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("summary", sa.Text),
        sa.Column("airdate", sa.String(20)),
        sa.Column("poster_url", sa.String(2000)),
        sa.Column("raw_payload", jsonb, nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_episode_cache_series_id", "episode_cache", ["series_id"])
    op.create_table(
        "watched_episodes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", uuid, nullable=False),
        sa.Column("episode_id", sa.Integer, nullable=False),
        sa.Column("watched", sa.Boolean, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "episode_id", name="uq_watched_user_episode"),
    )
    op.create_index("ix_watched_episodes_user_id", "watched_episodes", ["user_id"])
    op.create_index("ix_watched_episodes_episode_id", "watched_episodes", ["episode_id"])
    op.create_table(
        "comments",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("author_id", uuid, nullable=False),
        sa.Column("series_id", sa.Integer),
        sa.Column("episode_id", sa.Integer),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(series_id IS NULL) <> (episode_id IS NULL)", name="ck_comment_exactly_one_target"
        ),
    )
    op.create_index("ix_comments_author_id", "comments", ["author_id"])
    op.create_index("ix_comments_series_id", "comments", ["series_id"])
    op.create_index("ix_comments_episode_id", "comments", ["episode_id"])
    op.create_table(
        "insights",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("target_type", sa.String(20), nullable=False),
        sa.Column("target_id", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("used_fallback", sa.Boolean, nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("target_type", "target_id", name="uq_insight_target"),
    )


def downgrade() -> None:
    op.drop_table("insights")
    for index_name in ("ix_comments_episode_id", "ix_comments_series_id", "ix_comments_author_id"):
        op.drop_index(index_name, table_name="comments")
    op.drop_table("comments")
    for index_name in ("ix_watched_episodes_episode_id", "ix_watched_episodes_user_id"):
        op.drop_index(index_name, table_name="watched_episodes")
    op.drop_table("watched_episodes")
    op.drop_index("ix_episode_cache_series_id", table_name="episode_cache")
    op.drop_table("episode_cache")
    op.drop_table("series_cache")
    op.drop_table("users")
