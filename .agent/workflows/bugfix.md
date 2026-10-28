# Workflow — Bug fix

1. Reproduce. Write a failing test that captures the bug (`tests/unit/.../test_*.py`, name ends with
   `_regression_<issue>` if an issue exists). If it needs a document, add an anonymised fixture.
2. Find the root cause. Fix the cause, not the symptom. If the fix touches a stable contract, stop and ask.
3. Keep the diff minimal. No drive-by refactors (open a `refactor/` follow-up instead).
4. `make check` green. Add CHANGELOG entry under *Fixed*.
5. PR `fix(<scope>): <what was wrong>`; body states cause, fix, and how the test proves it.
