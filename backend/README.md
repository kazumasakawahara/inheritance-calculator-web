# Inheritance Calculator Web - Backend

FastAPI backend for the inheritance calculator web application.

## Features

- FastAPI-Users JWT authentication
- PostgreSQL for relational data (users, cases, persons)
- Neo4j for family tree graph relationships
- Integration with inheritance-calculator-core for calculation logic

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
uv run pytest

# Type checking
uv run mypy app

# Linting
uv run ruff check app
```

## Environment Variables

See `.env.example` for required environment variables.
