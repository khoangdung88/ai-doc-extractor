"""Explicit registry of document types. Adding a type = one line here (+ schema, prompt, tests)."""

from __future__ import annotations

from docext.core.errors import UnknownDocumentTypeError
from docext.domain.base import DocumentType
from docext.domain.booking_confirmation import BOOKING_CONFIRMATION_TYPE
from docext.domain.invoice import INVOICE_TYPE
from docext.domain.packing_list import PACKING_LIST_TYPE

DOCUMENT_TYPES: dict[str, DocumentType] = {
    t.name: t for t in (INVOICE_TYPE, PACKING_LIST_TYPE, BOOKING_CONFIRMATION_TYPE)
}


def get_document_type(name: str) -> DocumentType:
    try:
        return DOCUMENT_TYPES[name]
    except KeyError:
        raise UnknownDocumentTypeError(
            f"Unknown document type '{name}'",
            details={"available": sorted(DOCUMENT_TYPES)},
        ) from None


def list_document_types() -> list[DocumentType]:
    return list(DOCUMENT_TYPES.values())
