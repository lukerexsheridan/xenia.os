.DEFAULT_GOAL := help
SHELL := /bin/bash

BACKEND := backend
FRONTEND := frontend

# ── Meta ─────────────────────────────────────────────────────────────────────

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

.PHONY: setup
setup: ## Install backend + frontend dependencies and pre-commit hooks
	cd $(BACKEND) && uv sync
	cd $(FRONTEND) && npm install
	uv tool run pre-commit install

# ── Run ──────────────────────────────────────────────────────────────────────

.PHONY: dev
dev: ## Start the local stack (api, worker, postgres, minio)
	docker compose up --build

.PHONY: dev-backend
dev-backend: ## Run the API locally without Docker (needs a running Postgres)
	cd $(BACKEND) && uv run uvicorn app.main:app --reload --port 8000

.PHONY: dev-worker
dev-worker: ## Run the worker locally without Docker
	cd $(BACKEND) && uv run python -m app.workers.main

.PHONY: dev-frontend
dev-frontend: ## Run the Vite dev server
	cd $(FRONTEND) && npm run dev

.PHONY: down
down: ## Stop the local stack
	docker compose down

# ── Quality ──────────────────────────────────────────────────────────────────

.PHONY: lint
lint: ## Lint backend (ruff) and frontend (eslint)
	cd $(BACKEND) && uv run ruff check .
	cd $(FRONTEND) && npm run lint

.PHONY: format
format: ## Format backend (ruff) and frontend (prettier)
	cd $(BACKEND) && uv run ruff format .
	cd $(FRONTEND) && npm run format

.PHONY: format-check
format-check: ## Verify formatting without writing
	cd $(BACKEND) && uv run ruff format --check .
	cd $(FRONTEND) && npm run format:check

.PHONY: typecheck
typecheck: ## mypy --strict + tsc --noEmit
	cd $(BACKEND) && uv run mypy app tests
	cd $(FRONTEND) && npm run typecheck

.PHONY: import-lint
import-lint: ## Enforce the AP2 dependency direction (import-linter)
	cd $(BACKEND) && uv run lint-imports

.PHONY: test
test: ## Run backend (pytest) and frontend (vitest) tests
	cd $(BACKEND) && uv run pytest
	cd $(FRONTEND) && npm run test

.PHONY: coverage-domain
coverage-domain: ## Domain coverage gate (Doc 10 Epic 2 DoD: >=95%)
	cd $(BACKEND) && uv run pytest --cov=app.domain --cov-fail-under=95

.PHONY: check
check: lint format-check typecheck import-lint test ## Everything CI runs
	@echo "✓ all checks passed"

# ── Database ─────────────────────────────────────────────────────────────────

.PHONY: migrate
migrate: ## Apply migrations (alembic upgrade head)
	cd $(BACKEND) && uv run alembic upgrade head

.PHONY: revision
revision: ## New autogenerate revision: make revision m="message"
	cd $(BACKEND) && uv run alembic revision --autogenerate -m "$(m)"

.PHONY: migration-lint
migration-lint: ## Fail if models and migrations have drifted (alembic check)
	cd $(BACKEND) && uv run alembic check

# ── Artefacts ────────────────────────────────────────────────────────────────

.PHONY: openapi
openapi: ## Export the public OpenAPI schema to frontend/openapi.json
	cd $(BACKEND) && uv run python -m app.scripts.export_openapi ../frontend/openapi.json

.PHONY: build
build: ## Production builds (backend image requires Docker; frontend dist)
	docker build -t xenia-backend $(BACKEND)
	cd $(FRONTEND) && npm run build

.PHONY: clean
clean: ## Remove build artefacts and caches
	rm -rf $(BACKEND)/.venv $(BACKEND)/.mypy_cache $(BACKEND)/.ruff_cache $(BACKEND)/.pytest_cache
	rm -rf $(FRONTEND)/node_modules $(FRONTEND)/dist
