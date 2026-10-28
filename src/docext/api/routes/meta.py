"""Health and discovery endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from docext import __version__
from docext.core.config import get_settings
from docext.core.errors import UnknownProviderError
from docext.domain.registry import list_document_types
from docext.extraction.providers.registry import PROVIDERS, list_providers

router = APIRouter(tags=["meta"])


class DocumentTypeInfo(BaseModel):
    name: str
    title: str
    description: str
    prompt_version: str


class ProviderInfo(BaseModel):
    name: str
    requires_api_key: bool


class ServiceConfig(BaseModel):
    default_model: str
    providers: list[ProviderInfo]


class ModelList(BaseModel):
    provider: str
    models: list[str]


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@router.get("/v1/document-types", response_model=list[DocumentTypeInfo])
async def document_types() -> list[DocumentTypeInfo]:
    return [
        DocumentTypeInfo(
            name=t.name, title=t.title, description=t.description, prompt_version=t.prompt_version
        )
        for t in list_document_types()
    ]


@router.get("/v1/providers")
async def providers() -> list[str]:
    return list_providers()


@router.get("/v1/config", response_model=ServiceConfig)
async def service_config() -> ServiceConfig:
    """Non-sensitive discovery for clients (web UI): default model + provider key flags."""
    return ServiceConfig(
        default_model=get_settings().default_model,
        providers=[
            ProviderInfo(name=name, requires_api_key=PROVIDERS[name].requires_api_key)
            for name in list_providers()
        ],
    )


@router.get("/v1/models", response_model=ModelList)
async def provider_models(provider: str) -> ModelList:
    """Models a provider can enumerate itself (e.g. Ollama's /api/tags); else []."""
    cls = PROVIDERS.get(provider)
    if cls is None:
        raise UnknownProviderError(
            f"Unknown provider '{provider}'", details={"providers": sorted(PROVIDERS)}
        )
    return ModelList(provider=provider, models=await cls.list_models(get_settings()))
