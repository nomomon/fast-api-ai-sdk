.PHONY: help setup dev dev-backend dev-frontend build build-backend build-frontend
.PHONY: db db-stop lint lint-fix lint-backend lint-fix-backend lint-frontend lint-fix-frontend
.PHONY: format format-check format-backend format-check-backend format-frontend format-check-frontend
.PHONY: check check-fix check-backend check-fix-backend check-frontend check-fix-frontend
.PHONY: type-check type-check-backend type-check-frontend clean clean-backend clean-frontend

# Default target
help:
	@echo "Available targets:"
	@echo "  setup          - Setup backend virtual environment"
	@echo "  dev            - Start database and run both frontend/backend in parallel"
	@echo "  dev-backend    - Run only backend"
	@echo "  dev-frontend   - Run only frontend"
	@echo "  build          - Build both frontend and backend"
	@echo "  build-backend  - Build backend only"
	@echo "  build-frontend - Build frontend only"
	@echo "  db             - Start database container"
	@echo "  db-stop        - Stop database container"
	@echo "  lint           - Lint both frontend and backend"
	@echo "  lint-fix       - Lint and fix both frontend and backend"
	@echo "  format         - Format both frontend and backend"
	@echo "  format-check   - Check formatting for both frontend and backend"
	@echo "  check          - Run checks for both frontend and backend"
	@echo "  check-fix      - Run checks and fix for both frontend and backend"
	@echo "  type-check     - Type check both frontend and backend"
	@echo "  clean          - Clean build artifacts"

# Setup backend virtual environment & Frontend dependencies
setup:
	@make -C backend setup
	@cd frontend && pnpm install

# Database management
db:
	@docker-compose -f docker-compose.yml up -d postgres

db-stop:
	@docker-compose -f docker-compose.yml stop postgres

# Development targets
dev: setup db
	@echo "Starting frontend and backend in parallel..."
	@make -j2 dev-backend dev-frontend

dev-backend:
	@make -C backend dev

dev-frontend:
	@cd frontend && pnpm dev

# Build targets
build: build-backend build-frontend

build-backend:
	@make -C backend build

build-frontend:
	@cd frontend && pnpm build

# Linting targets
lint:
	@make -j2 lint-backend lint-frontend

lint-fix:
	@make -j2 lint-fix-backend lint-fix-frontend

lint-backend:
	@make -C backend lint

lint-fix-backend:
	@make -C backend lint-fix

lint-frontend:
	@cd frontend && pnpm lint

lint-fix-frontend:
	@cd frontend && pnpm lint:fix

# Formatting targets
format:
	@make -j2 format-backend format-frontend

format-check:
	@make -j2 format-check-backend format-check-frontend

format-backend:
	@make -C backend format

format-check-backend:
	@make -C backend format-check

format-frontend:
	@cd frontend && pnpm format

format-check-frontend:
	@cd frontend && pnpm format:check

# Check targets
check:
	@make -j2 check-backend check-frontend

check-fix:
	@make -j2 check-fix-backend check-fix-frontend

check-backend:
	@make -C backend check

check-fix-backend:
	@make -C backend check-fix

check-frontend:
	@cd frontend && pnpm check

check-fix-frontend:
	@cd frontend && pnpm check:fix

# Type checking targets
type-check:
	@make -j2 type-check-backend type-check-frontend

type-check-backend:
	@make -C backend type-check

type-check-frontend:
	@cd frontend && pnpm type-check

# Clean targets
clean:
	@make clean-backend clean-frontend

clean-backend:
	@make -C backend clean

clean-frontend:
	@cd frontend && pnpm clean
