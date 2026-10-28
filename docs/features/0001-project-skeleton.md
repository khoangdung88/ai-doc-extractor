# 0001 — Project skeleton

- **Status:** done
- **Owner:** @khoangdung88   **Agent:** Devin
- **Created:** 2026-10-28   **Related ADRs:** 0001–0005

## Problem
We need a foundation that lets AI agents add document types, model providers and input formats without
touching the core, and that keeps the codebase coherent over a long lifetime.

## Goal / Non-goals
- Goal: layered package, three plugin registries, working end-to-end path with a mock provider,
  API + CLI, CI with architecture guards, agent rules.
- Non-goals: production-grade providers' tuning, OCR, UI, persistence.

## Acceptance criteria
- [x] `make check` green
- [x] `uv run docext extract <pdf> --type invoice --model mock:echo` returns validated JSON
- [x] `POST /v1/extract` works with a PDF
- [x] Adding a document type / provider / loader requires no change to `pipeline.py`
