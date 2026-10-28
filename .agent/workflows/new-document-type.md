# Workflow — Add a new document type (e.g. Bill of Lading, Certificate of Origin)

Checklist — every item is required; the PR template asks for it.

1. **Domain research** → add/extend terms in `context/glossary.md`. List the fields with: name, type,
   required?, examples, and ambiguity notes (e.g. "gross vs net weight").
2. **Spec** in `docs/features/NNNN-doctype-<slug>.md` using `templates/feature-spec.md`. Include the field
   table and at least 3 anonymised sample documents you will use as fixtures.
3. **Schema**: `src/docext/domain/<slug>.py` with a Pydantic model `<Name>` inheriting `BaseDocumentSchema`,
   plus a `DocumentType` instance `<SLUG>_TYPE` (`name`, `schema`, `prompt_version`, `description`).
   Reuse shared value objects from `domain/common.py` (`Party`, `Money`, `Quantity`, `LineItem`, ...);
   add new ones there only if they are generic.
4. **Register** it in `domain/registry.py` (one line).
5. **Prompt**: `src/docext/extraction/prompts/<slug>/v1.md` from `templates/prompt-template.md`. Field
   rules must match the schema one-to-one.
6. **Fixtures**: `tests/fixtures/documents/<slug>/*.pdf` (synthetic/anonymised, < 500 KB) and golden
   outputs `tests/fixtures/golden/<slug>/*.json` produced by the `mock:fixture` provider.
7. **Tests**: schema validation tests (`tests/unit/domain/test_<slug>.py`), pipeline golden test, API
   smoke test for `type=<slug>`.
8. **Docs**: add the type to README's supported list and `docs/architecture.md` table; CHANGELOG entry.
9. **PR** `feat(domain): add <name> document type`.
