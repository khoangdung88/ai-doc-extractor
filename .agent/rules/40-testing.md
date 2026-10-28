# 40 — Testing rules

- Test pyramid: many unit tests (pure functions, schemas, pipeline with mock provider), a few integration
  tests (real providers, real PDFs), smoke test for API/CLI.
- Layout mirrors `src/`: `tests/unit/extraction/test_pipeline.py` tests `src/docext/extraction/pipeline.py`.
- Each test: one behavior, name reads as a sentence `test_<unit>_<behavior>_<condition>`. Arrange-Act-Assert
  separated by blank lines.
- Fixtures:
  - `tests/fixtures/documents/<doc_type>/` — small, **anonymised** sample files (synthetic company names,
    no real prices if they are confidential). Max 500 KB each. Add a `README.md` describing each file.
  - `tests/fixtures/golden/<doc_type>/<name>.json` — expected extraction output. Golden tests compare
    field-by-field and report diffs, not a single equality assert.
  - Shared pytest fixtures live in `tests/conftest.py`; keep them minimal.
- Every bug fix adds a regression test that fails before the fix.
- Mock at the boundary (provider, loader), never deep inside the module under test.
- Coverage is reported, not enforced as a gate; but new modules should be ~fully covered by unit tests.
- Flaky tests are bugs: fix or delete, never retry-loop.
