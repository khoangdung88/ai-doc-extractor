# ADR-0008: Self-hosted single-file web UI and per-request API keys

- **Status:** accepted
- **Date:** 2026-10-28
- **Deciders:** @khoangdung88, Devin

## Context
Operators need a GUI (roadmap #7): pick provider/model, supply credentials, upload several
PDFs, view extracted values. The repo forbids speculative dependencies and keeps contracts
minimal. API keys currently come only from env/`Settings` — a UI must let a user supply a key
without persisting it server-side. Feature spec: `docs/features/0005-web-ui.md`.

## Decision
We will serve ONE dependency-free `index.html` (vanilla JS/CSS) from the FastAPI app at
`GET /`, expose `GET /v1/config` for model/provider discovery, and accept an optional
`api_key` form field on `POST /v1/extract` that overrides the provider credential for that
request only via `Settings.model_copy` (provider → `Settings` field mapping lives in
`providers/registry.py::CREDENTIAL_SETTINGS`). `ModelProvider` gains a class-level
`requires_api_key` flag so the UI can show/hide the key field without instantiating providers
(their constructors already require the key). Keys are never stored, logged, or returned.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Single vanilla HTML file (chosen) | Zero deps/build; repo style; trivially reviewable | Manual DOM code; no component model |
| React/Vue SPA + toolchain | Rich UX later | Node toolchain, build step, new deps — heavyweight for this repo |
| Key stored in `.env` via settings endpoint | Survives restarts | Writes secrets to disk; multi-user unsafe |
| Per-request `api_key` field (chosen) | Nothing persisted; per-call control; easy to audit | Key re-entered each session; travels per request (HTTPS) |
| `requires_api_key` as class attribute (chosen) | Plugin metadata readable without instantiation | Slightly less structured than `ProviderCapabilities` |
| `requires_api_key` in `ProviderCapabilities` | Structured metadata | Needs an instance — constructor already requires the key |
| Key-field mapping kept in API layer | No contract change | Duplicates plugin knowledge outside the plugin |

## Consequences
- Positive: no new dependencies or build tooling; secrets never touch disk/logs; auto-detect
  (ADR-0007) makes multi-file upload trivial; additive changes keep existing clients intact.
- Negative / risks: keys transit per request (acceptable over HTTPS; documented); vanilla JS
  limits future UX richness — acceptable until roadmap #7 iterations demand more.
- Follow-ups (issues): HTTPS note for deployments; later iterations may add correction UI and
  then justify a real frontend toolchain.
