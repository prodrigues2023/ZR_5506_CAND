# Application package

The backend is organized using Clean Architecture boundaries:

- `domain/`
- `application/`
- `infrastructure/`
- `presentation/`

Domain rules and application use cases are kept independent from FastAPI,
PostgreSQL, TVMaze, and Hugging Face adapters. The presentation layer composes
these dependencies at the API boundary.
