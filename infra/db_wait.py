"""Single-loop PostgreSQL readiness probe."""

import asyncio
import os

import asyncpg


async def main() -> None:
    database_url = os.environ["SERIES_DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://")
    connection = await asyncpg.connect(database_url)
    await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
