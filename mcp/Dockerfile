FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Reuse the backend project definition so we can install fastmcp
WORKDIR /app
COPY backend/pyproject.toml backend/uv.lock* ./
COPY ai/ /ai/

RUN uv sync --frozen --no-dev --no-cache --no-editable

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY mcp/main.py mcp/workspace.py ./

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["python", "main.py"]

