"""Anthropic Messages API (REST). Structured output via a forced tool call whose input schema is the
document JSON schema, which yields strictly-typed JSON."""

from __future__ import annotations

import base64
import json
import time
from typing import Any

import httpx

from docext.core.config import Settings
from docext.core.errors import ProviderAuthError, ProviderError
from docext.extraction.providers._http import make_client, post_json
from docext.extraction.providers.base import (
    ExtractionRequest,
    ModelProvider,
    ProviderCapabilities,
    ProviderResponse,
    Usage,
)

_TOOL_NAME = "emit_document"


class AnthropicProvider(ModelProvider):
    name = "anthropic"
    requires_api_key = True

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        super().__init__(settings)
        if client is None:
            if not settings.anthropic_api_key:
                raise ProviderAuthError("ANTHROPIC_API_KEY is not set")
            client = make_client(
                settings,
                settings.anthropic_base_url,
                {"x-api-key": settings.anthropic_api_key, "anthropic-version": "2023-06-01"},
            )
        self._client = client

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(vision=True, json_mode=True, max_context_tokens=200_000)

    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse:
        content: list[dict[str, Any]] = [{"type": "text", "text": request.user_prompt}]
        for png in request.images_png:
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": base64.b64encode(png).decode(),
                    },
                }
            )
        payload: dict[str, Any] = {
            "model": request.model,
            "max_tokens": request.max_output_tokens,
            "temperature": request.temperature,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": content}],
            "tools": [
                {
                    "name": _TOOL_NAME,
                    "description": f"Emit the extracted {request.document_type} as JSON.",
                    "input_schema": request.json_schema,
                }
            ],
            "tool_choice": {"type": "tool", "name": _TOOL_NAME},
        }
        started = time.perf_counter()
        body = await post_json(
            self._client,
            "/v1/messages",
            payload,
            max_retries=self.settings.provider_max_retries,
            provider=self.name,
        )
        tool_input = next(
            (b.get("input") for b in body.get("content", []) if b.get("type") == "tool_use"), None
        )
        if not isinstance(tool_input, dict):
            raise ProviderError("anthropic: no tool_use block in response")
        usage = body.get("usage") or {}
        return ProviderResponse(
            raw_json=json.dumps(tool_input),
            model=f"anthropic:{body.get('model', request.model)}",
            usage=Usage(
                input_tokens=usage.get("input_tokens"), output_tokens=usage.get("output_tokens")
            ),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def close(self) -> None:
        await self._client.aclose()
