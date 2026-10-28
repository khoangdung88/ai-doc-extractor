"""OpenAI Chat Completions (REST) with JSON-schema structured output. Also works for any
OpenAI-compatible endpoint by setting OPENAI_BASE_URL."""

from __future__ import annotations

import base64
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


class OpenAIProvider(ModelProvider):
    name = "openai"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        super().__init__(settings)
        if client is None:
            if not settings.openai_api_key:
                raise ProviderAuthError("OPENAI_API_KEY is not set")
            client = make_client(
                settings,
                settings.openai_base_url,
                {"Authorization": f"Bearer {settings.openai_api_key}"},
            )
        self._client = client

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(vision=True, json_mode=True, max_context_tokens=128_000)

    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse:
        content: list[dict[str, Any]] = [{"type": "text", "text": request.user_prompt}]
        for png in request.images_png:
            b64 = base64.b64encode(png).decode()
            content.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        payload: dict[str, Any] = {
            "model": request.model,
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": content},
            ],
            "response_format": {"type": "json_object"},
        }
        started = time.perf_counter()
        body = await post_json(
            self._client,
            "/chat/completions",
            payload,
            max_retries=self.settings.provider_max_retries,
            provider=self.name,
        )
        try:
            text: str = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ProviderError("openai: unexpected response shape") from exc
        usage = body.get("usage") or {}
        return ProviderResponse(
            raw_json=text,
            model=f"openai:{body.get('model', request.model)}",
            usage=Usage(
                input_tokens=usage.get("prompt_tokens"),
                output_tokens=usage.get("completion_tokens"),
            ),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def close(self) -> None:
        await self._client.aclose()
