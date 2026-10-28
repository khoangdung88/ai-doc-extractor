"""Stable provider contracts (see ADR-0004)."""

from __future__ import annotations

import abc
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from docext.core.config import Settings


class ProviderCapabilities(BaseModel):
    model_config = ConfigDict(frozen=True)

    vision: bool = False
    json_mode: bool = False
    max_context_tokens: int | None = None


class ExtractionRequest(BaseModel):
    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    model: str
    system_prompt: str
    user_prompt: str
    json_schema: dict[str, Any]
    document_type: str
    source_name: str | None = None
    images_png: list[bytes] = Field(default_factory=list, repr=False)
    temperature: float = 0.0
    max_output_tokens: int = 8192


class Usage(BaseModel):
    model_config = ConfigDict(frozen=True)

    input_tokens: int | None = None
    output_tokens: int | None = None


class ProviderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    raw_json: str
    model: str
    usage: Usage = Field(default_factory=Usage)
    latency_ms: int = 0
    confidence: float | None = None


class ModelProvider(abc.ABC):
    """One vendor. Returns raw JSON text; the pipeline validates it against the schema."""

    name: str = "base"
    requires_api_key: bool = False

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    @abc.abstractmethod
    def capabilities(self) -> ProviderCapabilities: ...

    @classmethod
    async def list_models(cls, settings: Settings) -> list[str]:
        """Model names discoverable without credentials (e.g. a local model server).

        Empty list = no discovery; clients fall back to free-text model input.
        """
        return []

    @abc.abstractmethod
    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse: ...

    async def close(self) -> None:
        return None

    async def __aenter__(self) -> ModelProvider:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.close()
