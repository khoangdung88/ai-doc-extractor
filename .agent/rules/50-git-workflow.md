# 50 — Git & PR workflow

- `main` is always green and deployable. Direct pushes to `main` are forbidden; everything goes via PR + CI.
- Branch names: `feat/<short-slug>`, `fix/<slug>`, `refactor/<slug>`, `docs/<slug>`, `chore/<slug>`.
  Agents may prefix with their name, e.g. `devin/feat-<slug>`.
- Commits follow Conventional Commits: `feat(extraction): add retry on 429`, `fix(pdf): handle encrypted files`.
  Scopes = top-level module names (`core`, `domain`, `ingestion`, `extraction`, `api`, `cli`, `docs`, `agent`).
- One logical change per commit; commits should individually pass `make check` when practical.
- PR title = the conventional commit summary. Body follows `.github/PULL_REQUEST_TEMPLATE.md`.
- Link the spec/issue. A PR without a linked spec/issue is only acceptable for `chore`/`docs` under 50 lines.
- Squash-merge. The squash message is the PR title + body summary.
- Never force-push a shared branch. Never rewrite `main`.
- Labels: `feature`, `bug`, `refactor`, `docs`, `agent-rules`, `breaking`, `needs-adr`.
