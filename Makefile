.PHONY: install lint format typecheck test check run clean

install:        ## Install all deps (incl. dev) into .venv
	uv sync

lint:           ## Ruff lint
	uv run ruff check .

format:         ## Ruff format + autofix
	uv run ruff format . && uv run ruff check . --fix

typecheck:      ## mypy strict
	uv run mypy

test:           ## Unit tests (integration tests are skipped without API keys)
	uv run pytest

check: lint typecheck test   ## Everything CI runs

run:            ## Start API with reload
	uv run uvicorn docext.api.app:create_app --factory --reload --port 8000

clean:
	rm -rf .venv .mypy_cache .ruff_cache .pytest_cache dist build
