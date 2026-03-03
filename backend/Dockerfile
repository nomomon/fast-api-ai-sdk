FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy the ai package to /ai/ so uv can resolve the "../ai" path dependency
COPY ai/ /ai/

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --frozen --no-dev --no-cache --no-editable

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY backend/src ./src
COPY backend/alembic.ini .
COPY backend/alembic ./alembic

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
