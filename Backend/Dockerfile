FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY . /app

RUN uv run python scripts/seed_db.py

EXPOSE 7860

CMD ["/app/.venv/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
