# docext — AI document extraction for shipping documents

Extracts structured, validated JSON from **Invoice**, **Packing List** and **Booking Confirmation**
documents using pluggable AI models (OpenAI, Anthropic, Gemini, Ollama, ... or a mock for tests).
PDF is supported first; other formats are added as ingestion plugins.

## Quick start

```bash
# prerequisites: uv (https://docs.astral.sh/uv/)
make install
cp .env.example .env            # fill in the provider keys you use
make check                      # lint + typecheck + tests
make run                        # API on http://localhost:8000/docs — web UI on http://localhost:8000/

# CLI
uv run docext extract samples/invoice.pdf --type invoice --model openai:gpt-4o-mini
uv run docext extract combined.pdf --model openai:gpt-4o-mini   # omit --type to auto-detect
uv run docext providers         # list registered model providers
uv run docext types             # list registered document types
```

## How it works

```
file ──► ingestion (PDF → Document) ──► extraction pipeline ──► validated JSON
                                            │
                                            ├─ prompt for document type (domain registry)
                                            └─ ModelProvider plugin  (extraction/providers)
```

See [`docs/architecture.md`](docs/architecture.md) for details and [`docs/adr/`](docs/adr/) for decisions.

## Docker

```bash
docker build -t docext .
docker run -p 8000:8000 docext                       # mock model, no keys needed
docker run -p 8000:8000 --env-file .env docext       # with provider keys from .env
# UI on http://localhost:8000/ — API docs on /docs
```

Secrets are passed at runtime (`-e` / `--env-file`), never baked into the image.

## Web UI
`GET /` serves a single-page UI (no build step): pick provider/model, enter an API key (sent
per request, never stored), drop multiple PDFs — each is auto-classified per page — and view
every extracted field with warnings, skipped pages and raw JSON (spec 0005, ADR-0008).

## Developing with AI agents ("vibe coding")

This repo is designed to be developed mainly by AI coding agents with a human reviewer.
All agent rules are in [`AGENTS.md`](AGENTS.md) and [`.agent/`](.agent/). Start any task by
picking the matching workflow in `.agent/workflows/`:

| Task | Workflow |
|---|---|
| New feature | `.agent/workflows/new-feature.md` |
| New document type (e.g. Bill of Lading) | `.agent/workflows/new-document-type.md` |
| New AI model provider | `.agent/workflows/new-model-provider.md` |
| New input format (image, xlsx, ...) | `.agent/workflows/new-input-format.md` |
| Bug fix | `.agent/workflows/bugfix.md` |
| Refactor | `.agent/workflows/refactor.md` |

## Project layout

```
src/docext/
  core/         config, logging, errors
  domain/       Pydantic schemas per document type + registry
  ingestion/    loaders (pdf, ...) → Document
  extraction/   pipeline, prompts, providers/ (model plugins)
  api/          FastAPI
  cli.py        Typer CLI
tests/          unit / integration / fixtures
docs/           architecture, adr/, features/
.agent/         rules, workflows, templates, context for AI agents
.github/        CI, PR & issue templates
```

## License

MIT
