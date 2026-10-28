# ADR-0008: AI page classification and optional `type` on extract

- **Status:** accepted
- **Date:** 2026-10-28
- **Deciders:** @khoangdung88, Devin

## Context
Shipping PDFs frequently bundle several document types in one file. The pipeline is built as
1 file → 1 type → 1 `ExtractionResult`, with `type` mandatory on CLI and `POST /v1/extract`.
Manual pre-splitting (`scripts/extract_mixed_pdf.py`) works but pushes layout knowledge onto
the caller. Feature spec: `docs/features/0004-auto-document-type-detection.md`.

## Decision
We will add a classification stage inside `extraction/`: one extra `extract_structured` call
per document labels each page with a registered type or `unknown`; pages of the same type are
merged into one sub-`Document` and extracted normally. `type` becomes optional on CLI and
`POST /v1/extract`; the auto path returns a new `AutoExtractionResult`
(`results` + `skipped_pages`) while the explicit-`type` response stays unchanged.

## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| One classify call for all pages (chosen) | 1 extra request per file; simple JSON contract | Long PDFs may need snippet truncation |
| One classify call per page | Independent, cacheable | N extra requests; cost & latency |
| Heuristic/keyword rules | Free, deterministic | Brittle across layouts; owner asked for AI |
| New endpoint `/extract/auto` | No union response | Two entry points doing almost the same thing |
| `type` omitted → auto (chosen) | Mirrors CLI; minimal surface | Response shape varies with input |

## Consequences
- Positive: combined PDFs work end-to-end with zero caller knowledge; explicit-`type` callers
  are unaffected; no new dependencies or config.
- Negative / risks: one extra model call per auto request (cost/latency); union response on
  `POST /v1/extract` needs clear OpenAPI docs; misclassification merges wrong pages into a
  type — mitigated by `skipped_pages` reporting and future UI review (roadmap #7).
- Follow-ups (issues): tune page-snippet length and eval per-type accuracy once the eval
  harness (roadmap #2) exists; vision-based classification once page rendering lands (#3).
