import httpx

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


async def test_ai_uses_provider_response_when_available() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-token"
        return httpx.Response(200, json=[{"generated_text": "A concise insight."}])

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    generator = HuggingFaceInsightGenerator(
        Settings(
            huggingface_api_key="test-token",
            huggingface_api_url="https://huggingface.test/models",
            huggingface_model="test-model",
        ),
        client=client,
    )

    result = await generator.generate(
        target_type="series",
        target_id=139,
        title="Girls",
        summary="A story about friendship.",
        genres=("Drama",),
        comments=(),
    )
    await client.aclose()

    assert result.used_fallback is False
    assert result.text == "A concise insight."


async def test_ai_falls_back_when_provider_fails() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"error": "provider unavailable"})

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    generator = HuggingFaceInsightGenerator(
        Settings(
            huggingface_api_key="test-token",
            huggingface_api_url="https://huggingface.test/models",
            huggingface_model="test-model",
        ),
        client=client,
    )

    result = await generator.generate(
        target_type="episode",
        target_id=10,
        title="Pilot",
        summary="A story about friendship.",
        genres=("Drama",),
        comments=(),
    )
    await client.aclose()

    assert result.used_fallback is True
    assert "Pilot" in result.text
