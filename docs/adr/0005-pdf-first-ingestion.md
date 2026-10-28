# ADR-0005: PDF-first ingestion with PyMuPDF; `Document` contract
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
Most incoming documents are PDFs, both native-text and scanned. Other formats come later.
## Decision
`ingestion.Loader` plugins produce a `Document` (pages → text, optional PNG render, metadata). PyMuPDF is the
PDF engine (fast, renders pages for vision models, extracts text with layout). MIME is sniffed by content.
Scanned PDFs (no text layer) are flagged (`Document.metadata["has_text_layer"] = False`) so a vision/OCR
path can take over in a later feature.
## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| pdfplumber | nice tables | slower, no rendering |
| Unstructured/Docling | rich | heavy deps, less control |
## Consequences
AGPL licence of PyMuPDF must be respected (internal use fine; revisit before redistributing).
