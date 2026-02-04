# Database migrations

Schema changes are managed with [Alembic](https://alembic.sqlalchemy.org/). The application **does not** create tables on startup; you must run migrations in each environment.

## First-time setup

**IMPORTANT**: Before starting the application for the first time, you must run migrations to create the database schema. The application will fail to start without the necessary tables.

From the backend directory:

```bash
make migrate
```

Or directly:

```bash
alembic upgrade head
```

This applies all pending migrations and creates the required database tables.

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

## Configuration

The database URL is read from the environment (`DATABASE_URL`). Alembic loads `.env` from the backend or project root in `alembic/env.py`, so ensure `.env` or the environment is set before running Alembic.
