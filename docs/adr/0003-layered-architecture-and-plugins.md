# ADR-0003: Layered architecture with three plugin registries
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
Growth happens along three axes: document types, AI models, input formats. Without explicit seams,
agents will add `if/else` branches to the pipeline and the code will decay.
## Decision
Layers `api/cli → extraction → ingestion, domain → core` with one-way imports. Three explicit registries
(`domain/registry.py`, `extraction/providers/registry.py`, `ingestion/registry.py`). The pipeline never
branches on a concrete type/provider/format. CI greps for the main violations.
## Alternatives considered
| Option | Pros | Cons |
|---|---|---|
| Entry-point auto-discovery | zero-touch | magic, harder for agents to trace |
| Single flat module | fastest start | unmaintainable within weeks |
## Consequences
Adding a capability = add a module + one registry line + tests + docs, per `.agent/workflows/`.
