"""Use case for generating and caching AI insights."""

from collections.abc import Sequence

from app.application.contracts import GenerateInsightRequest, InsightResponse
from app.application.exceptions import InvalidRequest
from app.application.ports import (
    CommentRepository,
    InsightGenerator,
    InsightRepository,
    SeriesCatalog,
)


class GenerateInsight:
    def __init__(
        self,
        catalog: SeriesCatalog,
        comments: CommentRepository,
        insights: InsightRepository,
        generator: InsightGenerator,
    ) -> None:
        self.catalog = catalog
        self.comments = comments
        self.insights = insights
        self.generator = generator

    async def execute(self, request: GenerateInsightRequest) -> InsightResponse:
        if request.target_type not in {"series", "episode"}:
            raise InvalidRequest("Insight target must be series or episode")
        cached = await self.insights.get(request.target_type, request.target_id)
        if cached:
            return InsightResponse(cached)

        if request.target_type == "series":
            subject = await self.catalog.get_series(request.target_id)
            comment_values: Sequence[str] = ()
            if request.include_comments:
                comment_values = tuple(
                    comment.content for comment in await self.comments.list_for_series(subject.id)
                )
            insight = await self.generator.generate(
                target_type="series",
                target_id=subject.id,
                title=subject.title,
                summary=subject.summary,
                genres=subject.genres,
                comments=comment_values,
            )
        else:
            subject = await self.catalog.get_episode(request.target_id)
            series = await self.catalog.get_series(subject.series_id)
            comment_values = ()
            if request.include_comments:
                comment_values = tuple(
                    comment.content for comment in await self.comments.list_for_episode(subject.id)
                )
            insight = await self.generator.generate(
                target_type="episode",
                target_id=subject.id,
                title=subject.title,
                summary=subject.summary,
                genres=series.genres,
                comments=comment_values,
            )
        return InsightResponse(await self.insights.save(insight))
