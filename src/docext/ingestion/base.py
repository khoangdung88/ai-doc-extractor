"""Stable ingestion contracts: `Page`, `Document`, `Loader` (see ADR-0005)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field


class Page(BaseModel):
    model_config = ConfigDict(frozen=True)

    number: int = Field(ge=1)
    text: str = ""
    image_png: bytes | None = Field(default=None, repr=False, exclude=True)


class Document(BaseModel):
    """Format-agnostic representation handed to the extraction pipeline."""

    model_config = ConfigDict(frozen=True)

    filename: str | None = None
    mime_type: str
    pages: list[Page]
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def text(self) -> str:
        return "\n\n".join(f"--- page {p.number} ---\n{p.text}" for p in self.pages)

    @property
    def has_text_layer(self) -> bool:
        return any(p.text.strip() for p in self.pages)


@runtime_checkable
class Loader(Protocol):
    name: str

    def supports(self, mime_type: str, filename: str | None) -> bool: ...

    async def load(self, data: bytes, filename: str | None = None) -> Document: ...
