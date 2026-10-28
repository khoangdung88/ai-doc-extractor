"""Ingestion layer: turn raw bytes into a `Document` via format-specific `Loader` plugins.

Add a format via `.agent/workflows/new-input-format.md`.
"""

from docext.ingestion.base import Document, Loader, Page
from docext.ingestion.registry import load_document

__all__ = ["Document", "Loader", "Page", "load_document"]
