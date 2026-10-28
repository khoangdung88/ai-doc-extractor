import pytest

from docext.core.errors import UnknownDocumentTypeError
from docext.domain.base import BaseDocumentSchema
from docext.domain.registry import DOCUMENT_TYPES, get_document_type, list_document_types


def test_registry_contains_initial_document_types() -> None:
    assert {"invoice", "packing_list", "booking_confirmation"} <= set(DOCUMENT_TYPES)


def test_get_document_type_unknown_raises_with_available_list() -> None:
    with pytest.raises(UnknownDocumentTypeError) as exc:
        get_document_type("nope")

    assert "invoice" in exc.value.details["available"]  # type: ignore[operator]


def test_every_schema_produces_prompt_json_schema() -> None:
    for doc_type in list_document_types():
        assert issubclass(doc_type.schema, BaseDocumentSchema)
        schema = doc_type.schema.json_schema_for_prompt()

        assert schema["type"] == "object"
        assert "schema_version" in schema["properties"]
