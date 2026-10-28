# Architecture

> Keep this document current. If a PR changes structure, it changes this file.

## Goal
Turn shipping/trade documents (PDF first) into validated JSON for a given **document type** using a
configurable **AI model**, with a clean plugin seam for each of: document types, model providers,
input formats.

## Layers

```
┌───────────────────────── adapters ──────────────────────────┐
│  api/ (FastAPI + single-file UI)     cli.py (Typer)          │
└───────────────┬─────────────────────────────┬───────────────┘
                ▼                             ▼
┌───────────────────── extraction/ ───────────────────────────┐
│ pipeline.py  ─ orchestrates one extraction                  │
│ classification.py ─ per-page auto type detection            │
│ prompts/     ─ versioned prompt files + loader              │
│ providers/   ─ ModelProvider plugins (mock, openai, …)      │
│ json_repair.py ─ tolerant parsing of model output           │
└───────┬───────────────────────────────────┬─────────────────┘
        ▼                                   ▼
┌── ingestion/ ───────────┐   ┌── domain/ ──────────────────────┐
│ Loader plugins → Document│   │ Pydantic schemas per doc type   │
│ pdf.py, detect.py        │   │ DocumentType + registry         │
└───────────┬──────────────┘   └───────────────┬────────────────┘
            ▼                                  ▼
┌──────────────────────── core/ ──────────────────────────────┐
│ config (Settings), logging (structlog), errors               │
└─────────────────────────────────────────────────────────────┘
```

Dependency direction is top → bottom only (`.agent/rules/10-architecture.md`). CI enforces the main
violations with grep guards (`.github/workflows/ci.yml` → *architecture guard*).

## Request lifecycle (`POST /v1/extract`)

1. **Adapter** receives file bytes + optional `type` + optional `model`; validates size.
2. **Ingestion** sniffs MIME by content (`detect.py`), picks a `Loader`, returns a `Document`
   (pages with text, optional PNG renders for vision models, metadata).
3. **Pipeline** looks up the `DocumentType` (schema + prompt version), renders the prompt with the schema's
   JSON Schema and the document text, resolves `provider:model`, calls `ModelProvider.extract_structured`.
4. Model output → `json_repair.parse_json_output` → validated by the Pydantic schema → business-rule
   `warnings()` (e.g. totals mismatch).
5. **`ExtractionResult`** (data + model + prompt_version + usage + latency + warnings) is returned.

### Auto mode (`type` omitted — ADR-0008)

`extract_auto` first calls `classification.classify_pages`: one provider request labels every
page with a registry type or `unknown`. Pages of the same type are merged into one
sub-`Document` (wherever they appear) and extracted via the normal pipeline; unclassified
pages are reported in `AutoExtractionResult.skipped_pages`. One provider instance serves the
classify call and all extractions.

## Stable contracts (changing these needs an ADR)
- `ingestion.base.Document` / `Page`
- `extraction.pipeline.ExtractionResult`, `AutoExtractionResult`
- `extraction.providers.base.ModelProvider`, `ExtractionRequest`, `ProviderResponse`
- `domain.base.BaseDocumentSchema`, `DocumentType`
- Every document schema (`schema_version` field; breaking change → bump)

## Plugin registries
| Registry | File | Current entries |
|---|---|---|
| Document types | `domain/registry.py` | `invoice`, `packing_list`, `booking_confirmation` |
| Providers | `extraction/providers/registry.py` | `mock`, `openai`, `anthropic`, `ollama` |
| Loaders | `ingestion/registry.py` | `pdf` |

Providers talk to vendor **REST APIs via `httpx`** (no vendor SDKs required). An SDK-based provider is
allowed but must keep the SDK import inside its module and behind an optional extra.

## Configuration
`core/config.py::Settings` (env prefix `DOCEXT_`, `.env` supported). Vendor keys use vendor-standard names
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OLLAMA_BASE_URL`).

## Observability
structlog JSON logs in prod, console in dev. One `extraction_completed` / `extraction_failed` event per
extraction with `doc_type`, `model`, `prompt_version`, token usage and latency. Never logs document content.

## Not yet (see `roadmap.md`)
OCR / image input, vision-mode page images to models, async job queue for batch, persistence, web UI,
evaluation harness with field-level accuracy, auth.
