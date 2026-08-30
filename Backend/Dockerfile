FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . /app

RUN SQLALCHEMY_DATABASE_URI=sqlite:///CivicResolveAI.sqlite3 JWT_ACCESS_TOKEN_EXPIRES_DAYS=31 PORT=8000 COMMISSIONER_MAIL=comm@cr.com COMMISSIONER_PASSWORD=COM-001 COMMISSIONER_NAME=Sudo uv run python scripts/seed_db.py

EXPOSE 7860

CMD ["/app/.venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
