"""PDF loader backed by PyMuPDF: text layer per page, optional PNG renders for vision models."""

from __future__ import annotations

import asyncio
from typing import Any

from docext.core.errors import DocumentLoadError, EncryptedDocumentError
from docext.ingestion.base import Document, Page


class PdfLoader:
    name = "pdf"

    def __init__(self, *, render_images: bool = False, render_dpi: int = 110) -> None:
        self._render_images = render_images
        self._render_dpi = render_dpi

    def supports(self, mime_type: str, filename: str | None) -> bool:
        return mime_type == "application/pdf"

    async def load(self, data: bytes, filename: str | None = None) -> Document:
        return await asyncio.to_thread(self._load_sync, data, filename)

    def _load_sync(self, data: bytes, filename: str | None) -> Document:
        import pymupdf

        open_pdf: Any = pymupdf.open
        try:
            pdf = open_pdf(stream=data, filetype="pdf")
        except Exception as exc:
            raise DocumentLoadError(f"Cannot open PDF: {exc}") from exc
        with pdf:
            if pdf.is_encrypted and not pdf.authenticate(""):
                raise EncryptedDocumentError("PDF is password protected")
            pages: list[Page] = []
            for index, page in enumerate(pdf, start=1):
                text: str = page.get_text("text")
                image: bytes | None = None
                if self._render_images:
                    image = page.get_pixmap(dpi=self._render_dpi).tobytes("png")
                pages.append(Page(number=index, text=text, image_png=image))
            meta = {k: v for k, v in (pdf.metadata or {}).items() if v}
        document = Document(
            filename=filename,
            mime_type="application/pdf",
            pages=pages,
            metadata={"page_count": len(pages), "pdf_metadata": meta},
        )
        document.metadata["has_text_layer"] = document.has_text_layer
        return document
