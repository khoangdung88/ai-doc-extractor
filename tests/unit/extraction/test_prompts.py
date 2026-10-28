import pytest

from docext.domain.registry import list_document_types
from docext.extraction.prompts.loader import load_prompt


@pytest.mark.parametrize("doc_type", list_document_types(), ids=lambda t: t.name)
def test_every_document_type_has_a_loadable_prompt(doc_type) -> None:  # type: ignore[no-untyped-def]
    template = load_prompt(doc_type.name, doc_type.prompt_version)

    system, task = template.render(schema_json="{}", document_text="DOC", today="2026-01-01")

    assert "JSON" in system
    assert "DOC" in task
    assert "{{" not in system + task


def test_render_fails_on_missing_variable() -> None:
    template = load_prompt("invoice", "v1")

    with pytest.raises(KeyError):
        template.render(schema_json="{}")
