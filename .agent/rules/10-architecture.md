# 10 — Architecture rules

## Layers and dependency direction

```
api, cli  ──►  extraction  ──►  ingestion, domain  ──►  core
```

- Arrows mean "may import from". Nothing may import against the arrow. `core` imports nothing from `docext`.
- `domain` and `ingestion` do not know each other.
- `api`/`cli` are thin adapters: parse input → call `extraction.pipeline` → serialise output. No business logic.
- Cross-cutting concerns (config, logging, errors) live in `core` only.

## Plugin points (the only places that should grow with new capabilities)

| Capability | Interface | Registry | Add via workflow |
|---|---|---|---|
| AI model | `extraction/providers/base.py::ModelProvider` | `extraction/providers/registry.py` | `workflows/new-model-provider.md` |
| Document type | `domain/base.py::DocumentType` | `domain/registry.py` | `workflows/new-document-type.md` |
| Input format | `ingestion/base.py::Loader` | `ingestion/registry.py` | `workflows/new-input-format.md` |

- Registries are explicit (a dict populated at import in `registry.py`). No magic auto-discovery, no
  import-time side effects elsewhere.
- Core pipeline code must never `if provider == "openai"` or `if doc_type == "invoice"`. If you need that,
  the abstraction is missing a method — add it to the interface.

## Data contracts
- Every data structure crossing a layer boundary is a Pydantic model (or frozen dataclass for internal
  value objects). No raw dicts across boundaries.
- `Document` (ingestion output) and `ExtractionResult` (pipeline output) are the two stable contracts.
  Changing them requires an ADR.
- Schemas are versioned by the `schema_version` field; breaking changes bump it.

## Async and I/O
- Provider calls and ingestion are `async`. CPU-heavy work (PDF rendering) goes through
  `asyncio.to_thread`.
- No global mutable state except registries and settings (loaded once via `core.config.get_settings()`).

## Errors
- Raise typed exceptions from `core/errors.py` (`DocextError` subclasses). API maps them to HTTP in one place
  (`api/errors.py`). Never raise bare `Exception`; never swallow exceptions silently.

## Config
- All configuration via `core/config.py::Settings` (pydantic-settings, env prefix `DOCEXT_`). No `os.environ`
  reads elsewhere. Provider keys follow their vendor's standard env var names.
