"""Base classes shared by all document types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaseDocumentSchema(BaseModel):
    """Base for every extracted document.

    Fields are optional by design: a model must be able to say "not found" (null) rather than
    invent values."""

    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)

    schema_version: str = Field(default="1", description="Bump on breaking schema changes.")

    def warnings(self) -> list[str]:
        """Business-rule checks that do not invalidate the document (e.g. totals mismatch)."""
        return []

    @classmethod
    def json_schema_for_prompt(cls) -> dict[str, Any]:
        schema = cls.model_json_schema()
        schema.pop("title", None)
        return schema


@dataclass(frozen=True, slots=True)
class DocumentType:
    """Registry entry binding a name to a schema and a prompt version."""

    name: str
    title: str
    schema: type[BaseDocumentSchema]
    prompt_version: str
    description: str
