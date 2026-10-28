# 0006 — Web UI: review & edit extracted values against source text

- **Status:** in-progress
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** —   **Issue/PR:** —

## Problem
The UI (spec 0005) displays extracted fields read-only. Models still make mistakes — wrong
column, missed field, OCR-ish typos — and the operator has no way to verify a value against the
source document or correct it without hand-editing the downloaded JSON. This is the
review-and-correct half of roadmap #7 (edit was explicitly a non-goal of spec 0005).

## Goal / Non-goals
- Goal:
  - Every extracted leaf value renders as an **editable input** (text input / textarea) instead
    of static text — including nested objects (`shipper.name`) and array cells
    (`line_items[0].unit_price.amount`), nulls included so missing data can be filled in.
  - A **review tab**: "↗ review in new tab" opens a dedicated full-width page —
    embedded PDF left (~45%), editable fields right — for comfortable copy-compare.
    The child tab mutates the shared result object; Apply syncs back an `edited`
    badge on the main card via `window.opener`.
  - **Apply** merges edits into the in-memory result — the raw-JSON view and the download
    button then export the corrected data; card shows an "edited" marker.
- Non-goals (explicitly out of scope):
  - Server-side persistence of corrections (no job store yet — roadmap #6); "save" = apply to
    the result held in the page + download corrected JSON.
  - Adding/removing array rows or restructuring the JSON — v1 edits existing leaf values only.
  - Rendering the PDF via a JS library (no pdf.js dependency); the source pane uses the
    browser's built-in PDF viewer — note it shows the rendered pages, not the text layer.
  - Feeding corrections back into prompts/evals (later roadmap iteration).

## User flow
1. Extract as before → each detected document type section now renders a field table where
   every value cell is an input (null fields show an empty input).
2. User clicks **"↗ review in new tab"** on a document-type section → a full-width tab opens:
   PDF viewer left, editable field tree right; the user reads/copies the original while
   fixing values.
3. User clicks **Apply** (in the tab or in the card) → edited inputs are written back into
   `result.data` at their paths; the card gets an `edited` badge; raw JSON + download now
   contain the corrected data.

## Design
- Modules touched (respect `.agent/rules/10-architecture.md`):
  - `api/routes/preview.py` (new): `POST /v1/preview` — multipart file → `load_document` →
    `{filename, mime_type, pages: [{number, text}]}`. Same size guard as `/v1/extract`.
    Ingestion-only; no model call. Kept as the programmatic "what the model saw" accessor;
    the UI itself embeds the PDF client-side (no fetch needed).
  - `api/app.py`: register the preview router.
  - `api/ui/index.html`: render field cells as `<input>` bound to a JSON path
    (`data-path="shipper.name"`); "source text" toggle fetches + caches preview per card and
    lays out source fields side-by-side (flex, panes scroll independently); "Apply" walks the
    inputs, converts empty string → `null`, writes values back by path, sets an `edited`
    badge and refreshes the raw-JSON `<pre>`; download exports the edited object.
- Data contract changes: additive only — new `POST /v1/preview` response model
  (`DocumentPreview`). `Document`, `ExtractionResult`, `AutoExtractionResult` unchanged →
  no ADR needed.
- New dependencies: none. Config / env vars: none.
- Failure modes and errors:
  - Preview on unloadable/oversized file → same error envelope; shown in the source pane.
  - Apply with all-empty edits → no-op; badge unchanged.
  - Editing an array cell only touches that leaf; structure can't be broken by inputs.

## Acceptance criteria
- [x] `POST /v1/preview` returns per-page text for a PDF (test on synthetic fixture).
- [x] UI renders each leaf value as an input (verified manually: nested objects, arrays, nulls).
- [x] Source pane shows the same text the model saw and is copyable.
- [x] Apply writes edits into the result; raw JSON and downloaded file reflect them; an
      `edited` badge appears.
- [x] `make check` green.

## Test plan
Unit: `tests/unit/api/test_api.py` — preview endpoint returns page text and page count, 413 on
oversize, 415 on non-PDF. UI: manual verification (no JS toolchain, per spec 0005).

## Implementation plan
Ordered steps, each a commit:
1. This spec (approval gate).
2. `POST /v1/preview` route + `DocumentPreview` model + tests.
3. UI: editable cells + source pane + Apply/badge + raw-JSON refresh.
4. CHANGELOG + spec status update.

## Open questions
- Should Apply also POST the corrected JSON to the server (e.g. `POST /v1/feedback`) once a
  persistence layer (roadmap #6) exists — for evals/correction mining? Future iteration.
- Numeric/array-root edit affordances (add line item, delete row) if operators ask.
