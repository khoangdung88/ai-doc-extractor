# 00 — Core working rules

## Scope discipline
- Do exactly what the task/spec says. Unrelated improvements go to a new issue, not the current PR.
- If the spec is missing or ambiguous: write/complete the spec first (`templates/feature-spec.md`), get it
  approved (status `approved`), then code.
- Prefer deleting code over adding code. Prefer existing utilities over new ones.

## Change size
- Target PRs < 400 changed lines (excluding fixtures and lockfiles). Split larger work into a stack of PRs
  that each keep `main` green and shippable.
- Never mix refactor + behavior change in one commit. Refactor commits say `refactor:` and change no tests'
  expectations.

## Before writing code
1. Read `docs/architecture.md` and the module's `__init__.py` docstring.
2. `grep` for existing implementations of what you are about to write.
3. Write the test (or the fixture) that will prove the change.

## Before opening a PR
- `make check` is green. Fix root causes; never silence lint/mypy with blanket ignores.
- Update every doc the change makes stale in the same PR.
- Fill the PR template honestly, including "what I did not do".

## Communication
- When blocked or unsure, stop and ask a concrete question with options. Do not guess at product decisions
  (field semantics, output format, provider choice, pricing).
- Separate facts you verified (ran it, read it) from assumptions.
