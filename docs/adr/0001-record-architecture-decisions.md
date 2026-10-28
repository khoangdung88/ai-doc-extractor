# ADR-0001: Record architecture decisions
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
The project will be developed largely by AI agents across many sessions with no shared memory. Decisions
must be discoverable and their reasoning preserved.
## Decision
We will record every architecture-relevant decision as an ADR in `docs/adr/` using `.agent/templates/adr.md`.
## Consequences
Slight overhead per decision; much lower risk of agents re-litigating or silently reversing decisions.
