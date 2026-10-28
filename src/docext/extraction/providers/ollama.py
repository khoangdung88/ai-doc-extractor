"""Ollama local models via its REST API (`/api/chat`) with `format` = JSON schema."""

from __future__ import annotations

import base64
import time
from typing import Any

import httpx

from docext.core.config import Settings
from docext.core.errors import InputTooLargeError, ProviderError
from docext.extraction.providers._http import make_client, post_json
from docext.extraction.providers.base import (
    ExtractionRequest,
    ModelProvider,
    ProviderCapabilities,
    ProviderResponse,
    Usage,
)

# Ollama defaults `num_ctx` to 4096 and silently truncates the prompt beyond it, so the context
# window is sized per request. Token counts are upper-bound estimates: ~3 ASCII chars per token,
# 1 token per non-ASCII char (CJK, diacritics), and a flat budget per page image.
_ASCII_CHARS_PER_TOKEN = 3
_IMAGE_TOKENS = 1600
_NUM_CTX_FLOOR = 4096
_NUM_CTX_STEP = 1024
_NUM_CTX_SLACK = 512


def _estimate_text_tokens(text: str) -> int:
    non_ascii = sum(1 for ch in text if ord(ch) > 127)
    return (len(text) - non_ascii) // _ASCII_CHARS_PER_TOKEN + non_ascii


def estimate_num_ctx(request: ExtractionRequest, settings: Settings) -> int:
    """Context window to request from Ollama: forced override, or a prompt-sized upper bound.

    Raises `InputTooLargeError` when the bound exceeds `settings.ollama_max_num_ctx`, because Ollama
    would otherwise drop the tail of the prompt without reporting an error.
    """
    if settings.ollama_num_ctx is not None:
        return settings.ollama_num_ctx
    needed = (
        _estimate_text_tokens(request.system_prompt)
        + _estimate_text_tokens(request.user_prompt)
        + len(request.images_png) * _IMAGE_TOKENS
        + request.max_output_tokens
        + _NUM_CTX_SLACK
    )
    rounded = -(-needed // _NUM_CTX_STEP) * _NUM_CTX_STEP
    if rounded > settings.ollama_max_num_ctx:
        raise InputTooLargeError(
            f"Prompt needs ~{rounded} tokens of context, above DOCEXT_OLLAMA_MAX_NUM_CTX="
            f"{settings.ollama_max_num_ctx}",
            details={"estimated_tokens": rounded, "max_num_ctx": settings.ollama_max_num_ctx},
        )
    return max(rounded, _NUM_CTX_FLOOR)


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
