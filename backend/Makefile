.PHONY: help setup dev build lint lint-fix format format-check check check-fix type-check migrate migration migrate-downgrade clean

# Default target
help:
	@echo "Backend Makefile - Available targets:"
	@echo "  setup             - Install dependencies with uv"
	@echo "  dev               - Run development server"
	@echo "  build             - Build backend (placeholder)"
	@echo "  migrate           - Run database migrations (alembic upgrade head)"
	@echo "  migration         - Create new migration (use MSG=\"description\")"
	@echo "  migrate-downgrade - Roll back one migration (alembic downgrade -1)"
	@echo "  lint              - Lint code with ruff"
	@echo "  lint-fix          - Lint and fix code with ruff"
	@echo "  format            - Format code with ruff"
	@echo "  format-check      - Check code formatting"
	@echo "  check             - Run lint and format checks"
	@echo "  check-fix         - Run lint and format checks with fixes"
	@echo "  type-check        - Type check with mypy"
	@echo "  test              - Run tests"
	@echo "  clean             - Clean build artifacts and virtual environment"

# Install dependencies
setup:
	@uv sync

# Development server
dev:
	@uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Build (placeholder)
build:
	@echo 'Backend build complete'

# Database migrations (Alembic)
migrate:
	@uv run alembic upgrade head

migration:
	@if [ -z "$$MSG" ]; then echo 'Error: Pass migration message, e.g. make migration MSG="add foo column"'; exit 1; fi
	@uv run alembic revision --autogenerate -m "$$MSG"

migrate-downgrade:
	@uv run alembic downgrade -1

# Linting
lint:
	@uv run ruff check .

lint-fix:
	@uv run ruff check --fix .

# Formatting
format:
	@uv run ruff format .

format-check:
	@uv run ruff format --check .

# Check (lint + format check)
check:
	@uv run ruff check .
	@uv run ruff format --check .

check-fix:
	@uv run ruff check --fix .
	@uv run ruff format .

# Type checking
type-check:
	@uv run mypy src || true

# Tests
test:
	@PYTHONPATH=. uv run python -m unittest discover -s tests -p 'test_*.py' -v

# Clean
clean:
	@find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .venv
