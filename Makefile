# ═══════════════════════════════════════════════
# AI CyberShield — Makefile
# ═══════════════════════════════════════════════
# Development workflow commands.
# Usage: make <target>

.PHONY: install format lint test run clean help

# ──────────────────────────────────────────────
# Installation
# ──────────────────────────────────────────────

install: ## Install production dependencies
	pip install -r requirements.txt

install-dev: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e ".[dev]"

# ──────────────────────────────────────────────
# Formatting
# ──────────────────────────────────────────────

format: ## Format code with Black and sort imports with isort
	black .
	isort .

# ──────────────────────────────────────────────
# Linting
# ──────────────────────────────────────────────

lint: ## Run all linters (ruff + mypy)
	ruff check .
	mypy backend/ ml/

lint-fix: ## Run linters with auto-fix
	ruff check . --fix

# ──────────────────────────────────────────────
# Testing
# ──────────────────────────────────────────────

test: ## Run all tests with pytest
	pytest

test-coverage: ## Run tests with coverage report
	pytest --cov=backend --cov=ml --cov-report=term-missing

test-verbose: ## Run tests with verbose output
	pytest -v --tb=long

# ──────────────────────────────────────────────
# Running
# ──────────────────────────────────────────────

run: ## Start the FastAPI development server
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

run-prod: ## Start the FastAPI production server
	uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 4

run-docker: ## Start all services with Docker Compose
	docker-compose up --build

# ──────────────────────────────────────────────
# Cleaning
# ──────────────────────────────────────────────

clean: ## Clean cache, build artifacts, and temporary files
	rm -rf .venv/
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf logs/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

clean-docker: ## Clean Docker artifacts
	docker-compose down -v
	docker system prune -f

# ──────────────────────────────────────────────
# Help
# ──────────────────────────────────────────────

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
