# ADR-0002: Python 3.11 + FastAPI, uv, ruff, mypy strict
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
Document parsing and AI SDK ecosystems are strongest in Python. The team is small; agents write most code,
so tooling must catch mistakes mechanically.
## Decision
Python ≥ 3.11, FastAPI for the HTTP API, Typer for CLI, Pydantic v2 for all contracts. `uv` for env/lock,
`ruff` for lint+format, `mypy --strict`, `pytest`. Enforced in CI and pre-commit.
## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Node/TypeScript | great for UI | weaker PDF/ML libs, second language later for UI anyway |
| Django | batteries | heavier than needed for an API-first service |
## Consequences
Strict typing slows the first lines but keeps agent-written code honest; UI will be a separate package later.
