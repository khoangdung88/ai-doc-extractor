## What
<!-- One sentence. Title must be a Conventional Commit: feat(scope): ..., fix(scope): ... -->

## Why
<!-- Link the spec / issue / ADR. feat PRs without a spec are rejected by CI. -->
Spec/Issue: #
ADR: —

## How
<!-- Key design points a reviewer needs; which workflow in .agent/workflows you followed. -->

## What I did NOT do
<!-- Deferred scope, known gaps, follow-up issues. Be explicit. -->

## Checklist
- [ ] `make check` green locally
- [ ] Tests added/updated for every behavior change
- [ ] No vendor SDK outside `extraction/providers/`; dependency direction respected
- [ ] Docs updated (architecture / README / CHANGELOG / `.agent` if rules changed)
- [ ] No secrets, no real customer documents; fixtures anonymised
- [ ] Spec status updated (`approved` → `done`) if applicable
