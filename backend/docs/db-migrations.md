# Database migrations

Schema changes are managed with [Alembic](https://alembic.sqlalchemy.org/). The application **does not** create tables on startup; you must run migrations in each environment.

## First-time setup and deployment

**Run migrations before starting the application.** Tables are not created automatically. On first-time setup or after cloning the repo, run `make migrate` from the backend directory before starting the app. In deployment, run migrations as part of your release process (e.g. before starting the new process) so the database schema is up to date.

## Apply migrations

From the backend directory:

```bash
make migrate
```

Or directly:

```bash
alembic upgrade head
```

Run this after deploying or when pulling new migration files.

## Create a new migration

After changing SQLAlchemy models, generate a revision:

```bash
make migration MSG="short description of the change"
```

Or directly:

```bash
alembic revision --autogenerate -m "short description of the change"
```

Review the generated file in `alembic/versions/`, then apply it with `make migrate`.

## Roll back one migration

```bash
make migrate-downgrade
```

Or:

```bash
alembic downgrade -1
```

## Running migrations with Docker

When using Docker Compose, run migrations **before** or **after** the backend is up. The backend service uses `DATABASE_URL` (default: `postgresql://postgres:postgres@postgres:5432/fastapi_ai_sdk`).

**Option 1 – One-off migration (recommended for first deploy or after pulling):**

```bash
docker compose run --rm backend alembic upgrade head
```

This starts a temporary backend container, runs migrations, then exits. Use this when the backend is not running or when you want to run migrations in isolation.

**Option 2 – Inside a running backend container:**

If the backend service is already running:

```bash
docker compose exec backend alembic upgrade head
```

**Roll back one migration:**

```bash
docker compose run --rm backend alembic downgrade -1
```

Or, if the backend is running:

```bash
docker compose exec backend alembic downgrade -1
```

Ensure Postgres is up before running migrations (e.g. `docker compose up -d postgres`), or rely on `depends_on` when using `docker compose run` with the full stack.

## Configuration

The database URL is read from the environment (`DATABASE_URL`). Alembic loads `.env` from the backend or project root in `alembic/env.py`, so ensure `.env` or the environment is set before running Alembic.
