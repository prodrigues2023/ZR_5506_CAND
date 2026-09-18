# API Contract Draft

All application endpoints are prefixed with `/api`.

## Common behavior

- JSON request and response bodies.
- Validation errors return HTTP 422.
- Missing resources return HTTP 404.
- External provider failures are translated into stable application errors or fallback results.
- User-scoped endpoints establish/read the anonymous `user_id` HTTP-only cookie.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Application health check |
| GET | `/api/series/search?q=` | Search TVMaze series |
| GET | `/api/series/{series_id}` | Series details and episodes grouped by season |
| PUT | `/api/episodes/{episode_id}/watched` | Set watched state |
| GET | `/api/episodes/{episode_id}/watched` | Read watched state |
| GET | `/api/comments?series_id=` | List series comments |
| GET | `/api/comments?episode_id=` | List episode comments |
| POST | `/api/comments` | Add a comment to exactly one target |
| GET | `/api/series/{series_id}/insight` | Generate or retrieve series insight |
| GET | `/api/episodes/{episode_id}/insight` | Generate or retrieve episode insight |

## DTO sketches

```json
{
  "id": 139,
  "title": "Girls",
  "year": 2012,
  "poster_url": "https://...",
  "summary": "..."
}
```

```json
{
  "series": {},
  "seasons": [
    {
      "season": 1,
      "episodes": [
        {
          "id": 1,
          "number": 1,
          "title": "Pilot",
          "watched": false
        }
      ]
    }
  ]
}
```

```json
{
  "id": "uuid",
  "target_type": "series",
  "target_id": 139,
  "content": "Interesting premise.",
  "created_at": "2026-09-16T12:00:00Z"
}
```

```json
{
  "insight": "This series combines ...",
  "used_fallback": false
}
```
