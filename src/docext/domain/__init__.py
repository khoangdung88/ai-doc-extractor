"""Domain layer: document schemas (Pydantic) and the document-type registry.

Add a new document type via `.agent/workflows/new-document-type.md`.
"""

from docext.domain.base import BaseDocumentSchema, DocumentType
from docext.domain.registry import get_document_type, list_document_types

__all__ = ["BaseDocumentSchema", "DocumentType", "get_document_type", "list_document_types"]
