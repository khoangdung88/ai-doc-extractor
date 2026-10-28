# Workflow — Refactor

Refactor = behavior-preserving change. If any test expectation must change, it is not a refactor.

1. State the goal in the PR body in one sentence (e.g. "extract prompt rendering from pipeline so providers
   can reuse it"). If the goal needs an architecture change, write an ADR first.
2. Make sure the area is covered by tests before changing it; add characterisation tests if not.
3. Move in small commits, each `make check`-green. Rename/move in separate commits from logic changes so the
   diff is reviewable.
4. Update `docs/architecture.md` and import paths in `.agent/` docs if modules moved.
5. PR `refactor(<scope>): ...`. No feature flags, no new behavior.
