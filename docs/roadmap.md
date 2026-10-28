# Roadmap (living document — reorder freely, keep statuses honest)

| # | Milestone | Status |
|---|---|---|
| 0 | Skeleton: layers, registries, mock provider, PDF text ingestion, API + CLI, CI, agent rules | done |
| 1 | Real providers end-to-end (OpenAI, Anthropic, Ollama) with golden tests on synthetic PDFs | next |
| 2 | Evaluation harness: field-level accuracy per model/prompt version (`docs/evals/`) | planned |
| 3 | Scanned PDFs: page rendering → vision models; OCR fallback | planned |
| 4 | More input formats: images (jpg/png), xlsx, docx, .eml | planned |
| 5 | More document types: Bill of Lading, Certificate of Origin, Arrival Notice | planned |
| 6 | Batch / async jobs + persistence (job table, results store) | planned |
| 7 | Web UI for upload, review & correction (feedback loop into evals) | planned |
| 8 | Auth, multi-tenant config, per-tenant model routing & cost caps | planned |
