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

# Ollama defaults `num_ctx` to 4096 and silently truncates the prompt beyond it, so the context
# window is sized per request. ~3 chars/token is a conservative estimate for mixed text + JSON.
_CHARS_PER_TOKEN = 3
_NUM_CTX_FLOOR = 4096
_NUM_CTX_STEP = 1024
_NUM_CTX_SLACK = 512


def estimate_num_ctx(request: ExtractionRequest, settings: Settings) -> int:
    if settings.ollama_num_ctx is not None:
        return settings.ollama_num_ctx
    prompt_chars = len(request.system_prompt) + len(request.user_prompt)
    needed = prompt_chars // _CHARS_PER_TOKEN + request.max_output_tokens + _NUM_CTX_SLACK
    rounded = -(-needed // _NUM_CTX_STEP) * _NUM_CTX_STEP
    return min(max(rounded, _NUM_CTX_FLOOR), settings.ollama_max_num_ctx)


class OllamaProvider(ModelProvider):
    name = "ollama"

    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        super().__init__(settings)
        self._client = client or make_client(
            settings, settings.ollama_base_url, {}, timeout_s=settings.ollama_timeout_s
        )

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
                "num_ctx": estimate_num_ctx(request, self.settings),
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
