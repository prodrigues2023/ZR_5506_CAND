import httpx

from app.config import Settings
from app.infrastructure.tvmaze import TVMazeClient


async def test_tvmaze_search_maps_external_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/search/shows"
        assert request.url.params["q"] == "girls"
        return httpx.Response(
            200,
            json=[
                {
                    "show": {
                        "id": 139,
                        "name": "Girls",
                        "premiered": "2012-04-15",
                        "genres": ["Drama"],
                        "summary": "<p>A story</p>",
                        "image": {"medium": "https://example.com/girls.jpg"},
                    }
                }
            ],
        )

    client = TVMazeClient(
        Settings(tvmaze_base_url="http://tvmaze.test"),
        httpx.AsyncClient(base_url="http://tvmaze.test", transport=httpx.MockTransport(handler)),
    )
    results = await client.search("girls")

    assert results[0].title == "Girls"
    assert results[0].year == 2012
    assert results[0].summary == "A story"
