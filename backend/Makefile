.PHONY: help setup dev build lint lint-fix format format-check check check-fix type-check migrate migration migrate-downgrade clean

# Default target
help:
	@echo "Backend Makefile - Available targets:"
	@echo "  setup          - Setup virtual environment and install dependencies"
	@echo "  dev            - Run development server"
	@echo "  build          - Build backend (placeholder)"
	@echo "  migrate           - Run database migrations (alembic upgrade head)"
	@echo "  migration         - Create new migration (use MSG=\"description\")"
	@echo "  migrate-downgrade - Roll back one migration (alembic downgrade -1)"
	@echo "  lint           - Lint code with ruff"
	@echo "  lint-fix       - Lint and fix code with ruff"
	@echo "  format         - Format code with ruff"
	@echo "  format-check   - Check code formatting"
	@echo "  check          - Run lint and format checks"
	@echo "  check-fix      - Run lint and format checks with fixes"
	@echo "  type-check     - Type check with mypy"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean build artifacts and virtual environment"

# Setup virtual environment
setup:
	@if [ ! -d .venv ]; then python3 -m venv .venv; fi
	@.venv/bin/pip install --upgrade pip
	@.venv/bin/pip install -r requirements.txt

# Development server
dev:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Build (placeholder)
build:
	@echo 'Backend build complete'

# Database migrations (Alembic)
migrate:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/alembic upgrade head

migration:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@if [ -z "$$MSG" ]; then echo 'Error: Pass migration message, e.g. make migration MSG="add foo column"'; exit 1; fi
	@.venv/bin/alembic revision --autogenerate -m "$$MSG"

migrate-downgrade:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/alembic downgrade -1

# Linting
lint:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff check .

lint-fix:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff check --fix .

# Formatting
format:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff format .

format-check:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff format --check .

# Check (lint + format check)
check:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff check .
	@.venv/bin/ruff format --check .

check-fix:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/ruff check --fix .
	@.venv/bin/ruff format .

# Type checking
type-check:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@.venv/bin/mypy app || true

# Tests
test:
	@if [ ! -d .venv ]; then echo 'Error: Virtual environment not found. Run "make setup" first.'; exit 1; fi
	@PYTHONPATH=. .venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v

# Clean
clean:
	@find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .venv
