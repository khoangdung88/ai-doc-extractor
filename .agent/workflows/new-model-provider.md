# Workflow — Add a new AI model provider

1. **Spec** (short) in `docs/features/NNNN-provider-<slug>.md`: vendor, SDK + version, auth env var,
   structured-output mode available?, vision?, pricing notes, rate limits.
2. **ADR** if a new dependency is added (it almost always is) — `templates/adr.md`.
3. **Dependency**: add to `pyproject.toml` under `[project.optional-dependencies].<slug>` and to
   `all-providers`. Never to core dependencies.
4. **Implementation**: `src/docext/extraction/providers/<slug>.py` with class `<Name>Provider(ModelProvider)`.
   - Lazy SDK import inside the class, raising `ProviderNotInstalledError` with the `pip install docext[<slug>]` hint.
   - Implement `capabilities` (vision, json_mode, max_context_tokens), `extract_structured`, `close`.
   - Map vendor errors to `core.errors` types (`ProviderAuthError`, `ProviderRateLimitError`, `ProviderError`).
   - Return raw JSON text; do not validate against the schema.
5. **Register** in `providers/registry.py` (`PROVIDERS["<slug>"] = <Name>Provider`).
6. **Config**: document the env vars in `.env.example` and README.
7. **Tests**: unit test with the SDK client mocked (request building, error mapping, usage parsing);
   integration test under `tests/integration/providers/test_<slug>.py` skipped unless the key is set.
8. **Eval**: run the fixture set once, record results in `docs/evals/<date>-<slug>.md`.
9. **PR** `feat(extraction): add <name> provider`.
