# .agent/ — operating manual for AI agents

`AGENTS.md` (repo root) is the entry point. This directory holds the detail:

| Dir | What | When to read |
|---|---|---|
| `rules/` | Numbered topic rules. Lower number = more fundamental. | Always read `00` and `10`; read the others that match the files you touch. |
| `workflows/` | Step-by-step playbooks for recurring task types. | Pick exactly one at the start of a task and follow it. |
| `templates/` | Feature spec, ADR, prompt file templates. | When a workflow tells you to create one. |
| `context/` | Domain knowledge (shipping document glossary, field semantics). | When working on schemas or prompts. |

Rules for changing this directory itself:
- Rules are **short, imperative, and testable**. If a rule can't be checked in review, rewrite it or drop it.
- Changing a rule is a normal PR with the label `agent-rules`; explain *why* in the PR body.
- Keep the file numbering; insert new topics with a free number (e.g. `25-...`).
