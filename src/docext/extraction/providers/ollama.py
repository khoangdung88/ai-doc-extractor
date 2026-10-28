"""Ollama local models via its REST API (`/api/chat`) with `format` = JSON schema."""

from __future__ import annotations

import base64
import time
from typing import Any

import httpx

from docext.core.config import Settings
from docext.core.errors import ProviderError
from docext.extraction.providers._http import make_client, post_json
from docext.extraction.providers.base import (
    ExtractionRequest,
    ModelProvider,
    ProviderCapabilities,
    ProviderResponse,
    Usage,
)


class OllamaProvider(ModelProvider):
    name = "ollama"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        super().__init__(settings)
        self._client = client or make_client(settings, settings.ollama_base_url, {})

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(vision=True, json_mode=True)

    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse:
        user: dict[str, Any] = {"role": "user", "content": request.user_prompt}
        if request.images_png:
            user["images"] = [base64.b64encode(p).decode() for p in request.images_png]
        payload: dict[str, Any] = {
            "model": request.model,
            "stream": False,
            "format": request.json_schema,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_output_tokens,
            },
            "messages": [{"role": "system", "content": request.system_prompt}, user],
        }
        started = time.perf_counter()
        body = await post_json(
            self._client,
            "/api/chat",
            payload,
            max_retries=self.settings.provider_max_retries,
            provider=self.name,
        )
        try:
            text: str = body["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise ProviderError("ollama: unexpected response shape") from exc
        return ProviderResponse(
            raw_json=text,
            model=f"ollama:{body.get('model', request.model)}",
            usage=Usage(
                input_tokens=body.get("prompt_eval_count"), output_tokens=body.get("eval_count")
            ),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def close(self) -> None:
        await self._client.aclose()
