"""Health and discovery endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from docext import __version__
from docext.domain.registry import list_document_types
from docext.extraction.providers.registry import list_providers

router = APIRouter(tags=["meta"])


class DocumentTypeInfo(BaseModel):
    name: str
    title: str
    description: str
    prompt_version: str


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
