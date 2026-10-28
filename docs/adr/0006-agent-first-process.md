# ADR-0006: Agent-first development process
- **Status:** accepted  **Date:** 2026-10-28  **Deciders:** @khoangdung88
## Context
The codebase will be "vibe coded": AI agents implement, a human reviews. Agents lack memory across sessions
and tend to over-scope. Order must be enforced by the repository itself.
## Decision
- `AGENTS.md` is the single entry point; `.agent/rules` (topic rules), `.agent/workflows` (playbooks),
  `.agent/templates`, `.agent/context` hold detail. `CLAUDE.md`, `.cursor/rules`, `.github/copilot-instructions.md`
  only point to it.
- Spec-before-code: `feat` PRs must touch `docs/features/` or `docs/adr/` (CI check). Human approves specs.
- Small PRs, conventional commits, squash merge, CODEOWNERS on contracts and rules.
## Consequences
Slightly slower first commit per feature; far less drift, and any agent can pick up any task cold.
