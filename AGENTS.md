# AGENTS.md — rules for AI coding agents working in this repo

This file is the single entry point for every AI agent (Devin, Cursor, Copilot, Claude Code, Codex, ...).
Read it fully before touching code. Detailed rules live in `.agent/` and are referenced below.

## What this project is

`docext` extracts structured data from shipping/trade documents — **Invoice**, **Packing List**,
**Booking Confirmation** — using pluggable AI models. Input: PDF first; images/Excel/email later.
Output: validated JSON (Pydantic schemas in `src/docext/domain/`).

## Non-negotiables

1. **Read before you write.** Check `docs/architecture.md`, the relevant `.agent/rules/*.md`, and existing
   code in the module you are changing. Never duplicate something that already exists.
2. **One feature = one spec = one branch = one PR.** No spec in `docs/features/` → no feature code.
   Use `.agent/workflows/new-feature.md`. Small, reviewable PRs (< ~400 changed lines when possible).
3. **Respect the architecture.** Dependency direction is strictly
   `api / cli → extraction → ingestion, domain → core`. Never import "upwards". See `.agent/rules/10-architecture.md`.
4. **AI models are plugins.** All model access goes through `extraction/providers/base.py::ModelProvider`.
   Never call an SDK (openai, anthropic, ...) outside `extraction/providers/`.
5. **Document types are plugins.** A new document type = schema + prompt + registry entry + fixtures + tests.
   Follow `.agent/workflows/new-document-type.md`.
6. **Typed, validated, tested.** Full type hints, `mypy --strict` clean, `ruff` clean, tests for every
   behavior change. Run `make check` before opening a PR.
7. **No secrets, no customer documents in git.** Use `.env` (ignored) and anonymised fixtures only.
8. **Record decisions.** Anything that changes architecture, dependencies or data contracts gets an ADR
   in `docs/adr/` (template in `.agent/templates/adr.md`).
9. **Do not invent scope.** If the task is ambiguous, stop and ask; do not "improve" unrelated code.
10. **Leave the repo cleaner.** Update docs/README/CHANGELOG that the change makes stale, in the same PR.

## Where things are

| Path | Purpose |
|---|---|
| `src/docext/core/` | config, logging, errors — depends on nothing else in the project |
| `src/docext/domain/` | document schemas (Pydantic) + document-type registry |
| `src/docext/ingestion/` | loaders: bytes/file → `Document` (text + pages + metadata). PDF first |
| `src/docext/extraction/` | pipeline, prompt building, `providers/` (model plugins), post-validation |
| `src/docext/api/` | FastAPI app and routers (thin: parse request → call pipeline → return) |
| `src/docext/cli.py` | Typer CLI mirroring the API |
| `tests/unit`, `tests/integration`, `tests/fixtures` | tests; integration tests need API keys and are skipped otherwise |
| `docs/architecture.md` | the big picture — keep it current |
| `docs/adr/` | architecture decision records |
| `docs/features/` | one spec per feature (status: draft → approved → done) |
| `.agent/rules/` | detailed coding rules by topic |
| `.agent/workflows/` | step-by-step playbooks for common tasks |
| `.agent/templates/` | spec / ADR / prompt templates |
| `.agent/context/` | domain glossary and background knowledge |

## Commands

```bash
make install     # uv sync
make check       # ruff + mypy + pytest  (must pass before PR)
make run         # uvicorn on :8000
uv run docext extract path/to/file.pdf --type invoice --model mock:echo
```

## Definition of Done (every PR)

- [ ] Spec/issue linked, scope matches it exactly
- [ ] `make check` passes locally and in CI
- [ ] New behavior has unit tests; new doc type / provider has fixtures + golden tests
- [ ] Docs updated (`docs/architecture.md`, ADR, README, `.agent/` if rules changed)
- [ ] No secrets, no real customer data, no commented-out code, no TODO without an issue link
- [ ] PR description follows `.github/PULL_REQUEST_TEMPLATE.md`
