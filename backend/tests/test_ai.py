from app.config import Settings
from app.infrastructure.ai import HuggingFaceInsightGenerator


async def test_ai_uses_fallback_without_access_token() -> None:
    generator = HuggingFaceInsightGenerator(Settings(huggingface_api_key=None))
    result = await generator.generate(
        target_type="series",
        target_id=139,
        title="Girls",
        summary="A story about friendship.",
        genres=("Drama", "Comedy"),
        comments=(),
    )
    await generator.aclose()

    assert result.used_fallback is True
    assert "Girls" in result.text
    assert "Drama" in result.text
