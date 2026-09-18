"""Provider-independent AI insight adapters."""

from collections.abc import Sequence
from datetime import UTC, datetime

import httpx

from app.config import Settings
from app.domain.entities import Insight


def _fallback_text(title: str, summary: str | None, genres: Sequence[str]) -> str:
    genre_text = ", ".join(genres[:3]) or "character-driven storytelling"
    if summary:
        return (
            f"{title} blends {genre_text} with a story shaped by its central themes and characters."
        )
    return f"{title} explores {genre_text} through its characters, conflicts, and unfolding story."


class FallbackInsightGenerator:
    async def generate(
        self,
        *,
        target_type: str,
        target_id: int,
        title: str,
        summary: str | None,
        genres: Sequence[str],
        comments: Sequence[str],
    ) -> Insight:
        return Insight(
            target_type=target_type,
            target_id=target_id,
            text=_fallback_text(title, summary, genres),
            used_fallback=True,
            generated_at=datetime.now(UTC),
        )


class HuggingFaceInsightGenerator:
    """Hugging Face text-generation adapter with deterministic fallback."""

    def __init__(
        self,
        settings: Settings,
        client: httpx.AsyncClient | None = None,
        fallback: FallbackInsightGenerator | None = None,
    ) -> None:
        self.settings = settings
        self.client = client or httpx.AsyncClient(timeout=20)
        self.owns_client = client is None
        self.fallback = fallback or FallbackInsightGenerator()

    async def aclose(self) -> None:
        if self.owns_client:
            await self.client.aclose()

    async def generate(
        self,
        *,
        target_type: str,
        target_id: int,
        title: str,
        summary: str | None,
        genres: Sequence[str],
        comments: Sequence[str],
    ) -> Insight:
        if not self.settings.huggingface_api_key:
            return await self.fallback.generate(
                target_type=target_type,
                target_id=target_id,
                title=title,
                summary=summary,
                genres=genres,
                comments=comments,
            )
        prompt = self._prompt(title, summary, genres, comments)
        try:
            response = await self.client.post(
                f"{str(self.settings.huggingface_api_url).rstrip('/')}/{self.settings.huggingface_model}",
                headers={"Authorization": f"Bearer {self.settings.huggingface_api_key}"},
                json={"inputs": prompt, "parameters": {"max_new_tokens": 60}},
            )
            response.raise_for_status()
            text = self._extract_text(response.json())
            if not text:
                raise ValueError("Hugging Face returned no generated text")
            return Insight(target_type, target_id, text, False, datetime.now(UTC))
        except (httpx.HTTPError, ValueError, TypeError, KeyError):
            return await self.fallback.generate(
                target_type=target_type,
                target_id=target_id,
                title=title,
                summary=summary,
                genres=genres,
                comments=comments,
            )

    @staticmethod
    def _prompt(
        title: str, summary: str | None, genres: Sequence[str], comments: Sequence[str]
    ) -> str:
        comments_text = " | ".join(comments[:3]) or "No user comments available."
        return (
            "Write one concise sentence as a TV guide insight. Mention the themes or appeal, "
            "without spoilers.\n"
            f"Title: {title}\nGenres: {', '.join(genres) or 'Unknown'}\n"
            f"Summary: {summary or 'Unavailable'}\nComments: {comments_text}"
        )

    @staticmethod
    def _extract_text(payload: object) -> str | None:
        if isinstance(payload, list) and payload and isinstance(payload[0], dict):
            text = payload[0].get("generated_text")
            return text.strip() if isinstance(text, str) else None
        if isinstance(payload, dict):
            error = payload.get("error")
            if error:
                raise ValueError(str(error))
        return None
