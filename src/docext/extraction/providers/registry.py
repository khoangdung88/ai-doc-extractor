"""Explicit provider registry and `provider:model` resolution (the only place that parses it)."""

from __future__ import annotations

from docext.core.config import Settings, get_settings
from docext.core.errors import UnknownProviderError
from docext.extraction.providers.anthropic import AnthropicProvider
from docext.extraction.providers.base import ModelProvider
from docext.extraction.providers.mock import MockProvider
from docext.extraction.providers.ollama import OllamaProvider
from docext.extraction.providers.openai import OpenAIProvider

PROVIDERS: dict[str, type[ModelProvider]] = {
    MockProvider.name: MockProvider,
    OpenAIProvider.name: OpenAIProvider,
    AnthropicProvider.name: AnthropicProvider,
    OllamaProvider.name: OllamaProvider,
}

# Provider name -> Settings field holding its API credential. Used to apply a per-request
# `api_key` override (web UI, ADR-0009). Providers absent here take no key.
CREDENTIAL_SETTINGS: dict[str, str] = {
    "openai": "openai_api_key",
    "anthropic": "anthropic_api_key",
}


def resolve_model(spec: str) -> tuple[str, str]:
    """`"openai:gpt-4o-mini"` → `("openai", "gpt-4o-mini")`."""
    provider, sep, model = spec.partition(":")
    if not sep or not provider or not model:
        raise UnknownProviderError(
            f"Model must be '<provider>:<model>', got '{spec}'",
            details={"providers": sorted(PROVIDERS)},
        )
    if provider not in PROVIDERS:
        raise UnknownProviderError(
            f"Unknown provider '{provider}'", details={"providers": sorted(PROVIDERS)}
        )
    return provider, model


def create_provider(name: str, settings: Settings | None = None) -> ModelProvider:
    if name not in PROVIDERS:
        raise UnknownProviderError(
            f"Unknown provider '{name}'", details={"providers": sorted(PROVIDERS)}
        )
    return PROVIDERS[name](settings or get_settings())


def list_providers() -> list[str]:
    return sorted(PROVIDERS)
