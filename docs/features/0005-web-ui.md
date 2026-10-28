# 0005 — Web UI: model & API key picker, multi-file upload, results view

- **Status:** in-progress
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** 0009   **Issue/PR:** —

## Problem
`docext` is only reachable via CLI and raw HTTP. Operators who process shipments need a GUI to
pick the model + credentials, drop one or more PDFs (including combined invoice/packing-list
files), and read the extracted values — without touching a terminal or knowing document types
in advance. Roadmap #7.

## Goal / Non-goals
- Goal:
  - Single-page web UI served by the API itself at `GET /` — vanilla HTML/JS/CSS in ONE file,
    no frontend toolchain or new dependency.
  - Model selection: provider dropdown + model name input, prefilled from the server's current
    `default_model`; API key field for providers that need one.
  - API key is sent **per request** as an `api_key` form field — never stored, logged, or
    echoed back by the server.
  - Multi-file upload: one `POST /v1/extract` call per file with `type` omitted → the
    auto-detection from spec 0004 handles combined/single files uniformly.
  - Results view per file: detected type(s), field→value table, warnings, token usage,
    skipped pages, raw-JSON toggle, JSON download.
- Non-goals (explicitly out of scope):
  - Editing/correcting extracted values, feedback loop, auth/multi-user, job persistence
    (later roadmap #7 iterations).
  - Server-side storage of API keys (`.env` writing, session store) — keys live only in the
    request body.
  - A batch endpoint, upload progress websockets, OCR/image inputs.

## User flow
1. Open `http://localhost:8000/` → page loads `GET /v1/config`
   (`{default_model, providers: [{name, requires_api_key}]}`) and prefills provider/model.
2. User picks provider, adjusts model, enters API key (password field; shown only when
   `requires_api_key`; hint: "sent with each request, never stored").
3. User selects ≥1 PDF → clicks Extract → per-file status chip shows a live elapsed timer
   (processing → done/error, with total seconds).
4. Each finished file renders a card: one section per detected document type with a
   field→value table (nulls dimmed at the bottom), `warnings` highlighted, `skipped_pages`
   note, usage/latency footer, collapsible raw JSON and a download button.

## Design
- Modules touched (respect `.agent/rules/10-architecture.md`):
  - `extraction/providers/base.py`: class attribute `ModelProvider.requires_api_key`
    (set `True` in `openai`, `anthropic`) — readable without instantiation, since provider
    constructors already require the key. `extraction/providers/registry.py`:
    `CREDENTIAL_SETTINGS` maps provider name → `Settings` credential field.
  - `api/routes/meta.py`: `GET /v1/config` →
    `{"default_model": str, "providers": [{"name", "requires_api_key"}]}`;
    `GET /v1/models?provider=<name>` → provider-enumerable model list
    (`ModelProvider.list_models`, Ollama → `/api/tags`; `[]` ⇒ UI shows free-text input).
  - `api/routes/extract.py`: optional `api_key` Form field. When present and the resolved
    provider maps to a credential setting (`openai`→`openai_api_key`,
    `anthropic`→`anthropic_api_key`), the route builds `settings.model_copy(update=...)`
    and passes it through — pipeline/providers unchanged. Providers without a credential
    field ignore the key.
  - `api/ui/index.html` (new, single file) + `api/routes/ui.py`: `GET /` serves the page
    (read from package data, works from the installed wheel).
- Data contract changes: additive only — `POST /v1/extract` gains an optional form field,
  new `GET /v1/config`, `GET /`, provider class attribute → **ADR-0009**.
- New dependencies: none. Config / env vars: none.
- Failure modes and errors:
  - Missing/invalid key → provider auth error → per-file error card (existing error envelope).
  - Unloadable/oversized file → per-file error card; other files unaffected.
  - `api_key` sent to a keyless provider (`mock`, `ollama`) → silently ignored.
  - Key leakage: structlog never logs request bodies/headers; the UI keeps the key only in
    the input field (no localStorage).

## Acceptance criteria
- [x] `GET /` returns the UI page; `GET /v1/config` returns default model + provider/key flags.
- [x] Extract with `api_key` overrides the credential for that request only (test asserts the
      provider sees the override; subsequent requests use env settings).
- [x] UI: multi-file selection issues one auto-detect request per file and renders
      type sections with field→value tables, warnings, skipped pages, raw JSON.
- [x] No new dependencies; `make check` green.

## Test plan
Unit: `tests/unit/api/test_api.py` — `GET /`, `GET /v1/config` shape, `api_key` form accepted
and ignored for `mock`, credential override plumbing (monkeypatched provider factory).
UI correctness beyond serving is manual (no JS test toolchain — matches "no frontend
toolchain" decision).

## Implementation plan
Ordered steps, each a commit:
1. ADR-0009 + this spec (approval gate).
2. `ProviderCapabilities.requires_api_key` + `GET /v1/config` + `api_key` form override +
   tests.
3. `api/ui/index.html` + `GET /` route + tests.
4. README/screenshot note + CHANGELOG; architecture.md one-liner.

## Open questions
- Persist the chosen provider/model (not the key) in `localStorage` for convenience? v1: yes,
  harmless; revisit if operators object.
- Serve UI under `/ui` instead of `/` if a landing page is ever needed — keep `/` for now.
