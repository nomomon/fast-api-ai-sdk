.PHONY: help setup dev dev-backend dev-frontend db db-stop lint format check check-fix type-check clean

help:
	@echo "Available targets:"
	@echo "  setup       - Install all dependencies"
	@echo "  dev         - Start database, backend, and frontend"
	@echo "  db          - Start database container"
	@echo "  db-stop     - Stop database container"
	@echo "  lint        - Lint all packages"
	@echo "  format      - Format all packages"
	@echo "  check       - Lint + format check all packages"
	@echo "  check-fix   - Lint + format fix all packages"
	@echo "  type-check  - Type check all packages"
	@echo "  clean       - Clean build artifacts"

setup:
	@make -C ai setup
	@make -C backend setup
	@cd frontend && pnpm install

db:
	@docker-compose -f docker-compose.yml up -d postgres

db-stop:
	@docker-compose -f docker-compose.yml stop postgres

dev: setup db
	@make -j2 dev-backend dev-frontend

dev-backend:
	@make -C backend dev

dev-frontend:
	@cd frontend && pnpm dev

lint:
	@make -C ai lint
	@make -C backend lint
	@cd frontend && pnpm lint

format:
	@make -C ai format
	@make -C backend format
	@cd frontend && pnpm format

check:
	@make -C ai check
	@make -C backend check
	@cd frontend && pnpm check

check-fix:
	@make -C ai check-fix
	@make -C backend check-fix
	@cd frontend && pnpm check:fix

type-check:
	@make -C backend type-check
	@cd frontend && pnpm type-check

clean:
	@make -C ai clean
	@make -C backend clean
	@cd frontend && pnpm clean
