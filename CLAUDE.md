# Project Overview

Monorepo with three packages:

- **`ai/`** — standalone Python package: `AgentLoop`, `LLMProvider`, tools, skills, MCP
- **`backend/`** — FastAPI app (Python, uv, ruff, mypy)
- **`frontend/`** — Next.js app (pnpm, Biome)

## Key Commands

```bash
make setup        # install all dependencies
make dev          # start db + backend + frontend
make check-fix    # lint + format (all packages)
make type-check   # mypy (backend) + tsc (frontend)
```

Backend only (from `backend/`):

```bash
uv run uvicorn src.main:app --reload
uv run ruff check --fix . && uv run ruff format .
make migrate      # alembic upgrade head
make test
```

Git hooks (lefthook) run automatically on commit/push:

- **pre-commit**: lint + format fix for all packages, lockfile sync
- **pre-push**: lint + format check for all packages

## Architecture

### `ai/` package

The agent loop is format-independent — it yields typed dataclass events (`TextDelta`, `ToolInputDelta`, `Finish`, etc.) defined in `ai/ai/agent/events.py`. Consumers convert these to their wire format.

- `AgentLoop` — `ai/ai/agent/loop.py`
- `LLMProvider` (ABC) + `LiteLLMProvider` — `ai/ai/providers/`
- `Tool` base class — `ai/ai/agent/tools/base.py`
- `AgentEvent` types — `ai/ai/agent/events.py`
- `SystemPrompt` (composable prompt builder) + message helpers — `ai/ai/agent/context.py`
- Skills system — `ai/ai/agent/skills/` (`SkillsLoader`, `FileSkillSource`, `SkillSource` ABC)
- MCP client + tool wrapper — `ai/ai/mcp/`

### Backend (`backend/src/`)

- `ai/route.py` — chat endpoint (`POST /api/ai`), streams SSE
- `ai/handler.py` — `run_agent()` orchestrator: loads skills/MCPs, builds system prompt, runs AgentLoop
- `ai/formatter.py` — converts `AgentEvent`s to SSE format
- `ai/adapters/messages.py` — converts client messages to OpenAI format
- `ai/skills/` — user skill CRUD (DB models, repository, route, schemas)
- `ai/mcp/` — user MCP config CRUD (DB models, repository, route, schemas)
- `ai/models/` — available LLM model registry (repository, route, schemas)
- `ai/prompts/` — prompt templates from markdown files (`expert.md`, `concise.md`, `none.md`)
- `ai/tools.py` — `LoadSkillTool`, `UpdateSkillTool`
- `auth/` — JWT-based auth (login, signup, dependencies)
- `user/` — user models, repository, service

### Frontend (`frontend/`)

- `app/(app)/` — main app routes (chat, dashboard)
- `app/(auth)/` — login/signup pages
- `app/api/[...path]/` — proxy to backend API
- `components/chat/` — chat interface (uses Vercel AI SDK `useChat`)
- `components/skill/` — skill management dashboard + CRUD dialogs
- `components/mcp/` — MCP configuration dashboard + CRUD dialogs
- `components/ui/` — Radix UI primitives (shadcn/ui)
- `lib/hooks/` — `use-skills`, `use-mcps`, `use-available-models`, `use-available-prompts`, `use-user`
- `lib/api-client.ts` — HTTP client for backend calls

## Conventions

- Python: ruff for lint/format, mypy for types
- Frontend: Biome for lint/format, TypeScript strict mode
- Backend uses `uv` — always `uv run <cmd>`, never activate venv manually
- No direct commits — use branches
