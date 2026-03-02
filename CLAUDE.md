# Project Overview

Monorepo with three packages:

- **`ai/`** — standalone Python package: `AgentLoop`, `LLMProvider`, tools, skills
- **`backend/`** — FastAPI app (Python, uv, ruff, mypy)
- **`frontend/`** — Next.js app (pnpm)

## Key Commands

```bash
make dev          # start db + backend + frontend
make check-fix    # lint + format (both)
make type-check   # mypy (backend) + tsc (frontend)
```

Backend only (from `backend/`):
```bash
uv run uvicorn src.main:app --reload
uv run ruff check --fix . && uv run ruff format .
make migrate      # alembic upgrade head
make test
```

## Architecture

### `ai/` package

The agent loop is format-independent — it yields typed dataclass events (`TextDelta`, `ToolInputDelta`, `Finish`, etc.) defined in `ai/ai/agent/events.py`. Consumers convert these to their wire format.

- `AgentLoop` — `ai/ai/agent/loop.py`
- `LLMProvider` (ABC) + `LiteLLMProvider` — `ai/ai/providers/`
- `Tool` base class — `ai/ai/agent/tools/base.py`
- `AgentEvent` types — `ai/ai/agent/events.py`
- Message helpers — `ai/ai/agent/context.py`

### Backend (`backend/src/`)

- `chat/` — router + service (orchestrates agent calls)
- `ai/agents/` — `ChatAgent` (current), to be replaced by `AgentLoop` from `ai/`
- `ai/tools/` — tool definitions and registry
- `ai/adapters/` — message conversion, SSE formatting
- `skill/`, `mcp/` — skill storage, MCP tool support

## Conventions

- Python: ruff for lint/format, mypy for types
- Backend uses `uv` — always `uv run <cmd>`, never activate venv manually
- No direct commits — use branches
