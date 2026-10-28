# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed
- `ollama` provider: send `"think": false` — thinking models (qwen3-*, deepseek) emitted
  reasoning before JSON and broke `extraction_validation_failed` on otherwise valid output.
- `ollama` provider: dedicated `DOCEXT_OLLAMA_TIMEOUT_S` (default 300 s) so cold model loads no
  longer hit the shared 60 s timeout; `options.num_ctx` is now sized from the prompt (override with
  `DOCEXT_OLLAMA_NUM_CTX`, cap with `DOCEXT_OLLAMA_MAX_NUM_CTX`) instead of Ollama's silent 4096 default;
  prompts that cannot fit the cap fail with `input_too_large` instead of being truncated.

### Added
- Review & edit in the web UI: every extracted leaf value renders as an editable input
  (nested objects, array cells, nulls); **↗ review in new tab** opens a full-width page
  with the source PDF beside the fields; **Apply edits** writes changes back into the
  result JSON with an `edited` badge — raw view and download reflect them (spec 0006).
  `POST /v1/preview` returns per-page text for programmatic access.
- `Dockerfile` + `.dockerignore`: two-stage `uv` build (locked deps, `--no-editable` install,
  non-root runtime) — `docker build -t docext . && docker run -p 8000:8000 docext` serves API
  and UI on :8000.
- Web UI at `GET /`: single-file page (no frontend toolchain) to pick provider/model, supply
  an API key per request (`api_key` form field — never stored or logged), upload multiple
  PDFs that are auto-classified, and view extracted fields, warnings, skipped pages and raw
  JSON; new `GET /v1/config` discovery endpoint (spec 0005, ADR-0008).
- Auto document-type detection: omitting `--type` (CLI) or `type` (`POST /v1/extract`) runs one
  AI classification call that labels every page with a registered type or `unknown`, merges
  pages of the same type into one extraction, and returns `AutoExtractionResult`
  (`results` + `skipped_pages`) — combined PDFs like invoice + packing list now work
  end-to-end (spec 0004, ADR-0007).
- `invoice` schema v2 / prompt v2: `LineItem.part_number` and `LineItem.price_components` for
  multi-column (processing-trade) prices, `contract_number`, `shipped_per`, `shipment_date`,
  `amount_components`, `total_packages`, `net_weight`, `gross_weight`; warning when
  `quantity x unit_price` differs from `amount`; prompt forbids invented zero charges; synthetic
  processing-invoice fixture and golden file (spec 0003).
- `booking_confirmation` schema v2 / prompt v2 with air-freight support: `transport_mode`,
  `booking_reference`, `mawb_number`, `hawb_number`, `flight_number`, `cargo_cutoff`, `terminal`,
  `pieces`, `chargeable_weight`, `ex_factory_date`; mode-consistency warnings; synthetic air fixture
  and golden files (spec 0002).
- Project skeleton: core config/logging, domain schemas (invoice, packing list, booking confirmation),
  PDF ingestion, extraction pipeline with `ModelProvider` plugin interface and `mock` provider,
  FastAPI `/v1/extract` endpoint, Typer CLI, CI, agent rules (`AGENTS.md`, `.agent/`).
