# 0004 — Auto document-type detection for combined PDFs

- **Status:** in-progress
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** 0008   **Issue/PR:** —

## Problem
Real shipments often arrive as **one PDF containing several document types** (e.g. invoice on
page 1, packing list on pages 2–3). Today `type` is mandatory in both CLI (`--type`) and API
(`POST /v1/extract` form field), so the caller must know the layout in advance and manually
split the file (see `scripts/extract_mixed_pdf.py`). Users want to upload a combined file and
let an AI model detect which pages belong to which document type.

## Goal / Non-goals
- Goal: omitting `type` triggers an AI classification step that labels every page with a
  registered document type (or `unknown`), groups pages by type, and runs the normal extraction
  pipeline once per detected type. Pages that cannot be classified are skipped and reported.
- Non-goals (explicitly out of scope):
  - Scanned/image PDFs (classification needs a text layer; vision classify waits for roadmap #3).
  - Per-segment extraction of non-contiguous runs — pages of the same type are **merged** into
    one extraction, wherever they appear (decided with owner).
  - A separate, cheaper classifier model — classification reuses the model chosen for
    extraction (`--model` / `DOCEXT_DEFAULT_MODEL`), no new config.
  - Changing behavior when `type` IS given (single-type path is untouched).

## User flow
CLI — `type` becomes optional:
```bash
uv run docext extract combined.pdf                 # auto-detect
uv run docext extract combined.pdf --type invoice  # unchanged single-type path
```
Auto output:
```json
{"results": [<ExtractionResult for invoice>, <ExtractionResult for packing_list>],
 "skipped_pages": [{"pages": [5], "reason": "unrecognized document type"}]}
```
API — `POST /v1/extract` with `type` omitted returns the same body instead of a bare
`ExtractionResult`. With `type` present the response is unchanged (backward compatible).

## Design
- Modules touched (respect `.agent/rules/10-architecture.md`):
  - `core/errors.py`: new `ClassificationError` (subclass of `DocextError`).
  - `extraction/classification.py` (new): `classify_pages(document, provider, model, settings)
    -> dict[int, str]`. Sends **one** `extract_structured` request through the existing
    `ModelProvider` abstraction — page number + first ~1200 chars of each page's text — asking
    for `{"labels": [{"page": 1, "type": "invoice"}, ...]}` where `type` is a registry name or
    `"unknown"`. Labels outside the registry are coerced to `"unknown"`; pages the model omits
    default to `"unknown"`; out-of-range page numbers are dropped.
  - `extraction/prompts/classify/v1.md` (new): classification prompt via the existing
    `load_prompt("classify", "v1")` mechanism; enumerates types from `domain.registry`.
  - `extraction/pipeline.py`: new `AutoExtractionResult` model
    (`results: list[ExtractionResult]`, `skipped_pages: list[SkippedPages]`) and
    `extract_auto(document, model, ...)`: classify → group page numbers per known type →
    build a sub-`Document` per type (same pattern as `scripts/extract_mixed_pdf.py`) →
    `extract()` each, reusing ONE provider instance for classify + all extractions.
  - `api/routes/extract.py`: `type` Form becomes optional; returns
    `ExtractionResult | AutoExtractionResult`.
  - `cli.py`: `--type` optional; auto path prints the `AutoExtractionResult` JSON.
- Data contract changes: `ExtractionResult` unchanged; `Document` unchanged. NEW response type
  `AutoExtractionResult` and a response-variant change on `POST /v1/extract` → **ADR-0008**.
- New dependencies: none. Config / env vars: none.
- Failure modes and errors:
  - PDF has no text layer → `ClassificationError` ("cannot auto-detect without a text layer;
    pass --type explicitly").
  - Classifier returns invalid JSON → `ClassificationError` (no retry in v1).
  - Every page `unknown` → 200/exit 0 with `results: []` and all pages in `skipped_pages`.
  - Extraction of one detected type fails → propagate existing errors (no partial masking).

## Acceptance criteria
- [x] `docext extract combined.pdf` (no `--type`) on a synthetic 2-type PDF returns one
      `ExtractionResult` per type with `pages` matching the classified page set.
- [x] `POST /v1/extract` without `type` returns `{"results": [...], "skipped_pages": [...]}`;
      with `type` returns the unchanged single result.
- [x] An unrecognized page lands in `skipped_pages` and does not fail the request.
- [x] Exactly ONE provider instance is used for classify + all extractions (test asserts).
- [x] `make check` green.

## Test plan
Unit: `tests/unit/extraction/test_classification.py` (label parsing, unknown/out-of-range
clamping via `mock:canned`), `tests/unit/extraction/test_pipeline_auto.py` (grouping, merge
same-type pages, provider reuse). API/CLI: extend existing route/CLI tests for the optional
`type`. Fixtures: extend `scripts/make_sample_pdfs.py` with a combined 3-page synthetic PDF
(invoice + packing_list + unrecognized page). No real customer data.

## Implementation plan
Ordered steps, each a commit:
1. ADR-0008 + this spec (approval gate).
2. `ClassificationError`, `SkippedPages`/`AutoExtractionResult`, classify prompt v1,
   `classification.py` + unit tests.
3. `pipeline.extract_auto` + tests.
4. CLI `--type` optional + API optional `type` union response + tests.
5. Combined synthetic fixture, README/CHANGELOG, architecture.md update.

## Open questions
- Page text snippet cap (~1200 chars) — tune once eval harness (roadmap #2) exists.
- Later: report per-page labels in `skipped_pages`/results metadata for UI review (roadmap #7)?
