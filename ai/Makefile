.PHONY: help setup lint lint-fix format format-check check check-fix clean

# Default target
help:
	@echo "AI package Makefile - Available targets:"
	@echo "  setup         - Install dependencies with uv"
	@echo "  lint          - Lint code with ruff"
	@echo "  lint-fix      - Lint and fix code with ruff"
	@echo "  format        - Format code with ruff"
	@echo "  format-check  - Check code formatting"
	@echo "  check         - Run lint and format checks"
	@echo "  check-fix     - Run lint and format checks with fixes"
	@echo "  clean         - Clean build artifacts"

# Install dependencies
setup:
	@uv sync

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

# Clean
clean:
	@find . -type d -name '__pycache__' -exec rm -r {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@rm -rf .venv
