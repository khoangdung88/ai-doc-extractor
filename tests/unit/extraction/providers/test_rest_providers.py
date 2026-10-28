"""Provider unit tests with the vendor API mocked at the HTTP boundary."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from docext.core.config import Settings
from docext.core.errors import ProviderAuthError, ProviderError, ProviderRateLimitError
from docext.extraction.providers.anthropic import AnthropicProvider
from docext.extraction.providers.base import ExtractionRequest
from docext.extraction.providers.ollama import OllamaProvider
from docext.extraction.providers.openai import OpenAIProvider

REQUEST = ExtractionRequest(
    model="m",
    system_prompt="sys",
    user_prompt="user",
    json_schema={"type": "object"},
    document_type="invoice",
)


def client_returning(
    status: int, body: dict[str, Any], seen: list[dict[str, Any]]
) -> httpx.AsyncClient:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(json.loads(request.content))
        return httpx.Response(status, json=body)

    return httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://test")


async def test_openai_builds_request_and_parses_usage(settings: Settings) -> None:
    seen: list[dict[str, Any]] = []
    body = {
        "model": "gpt-x",
        "choices": [{"message": {"content": '{"invoice_number": "A"}'}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
    }
    provider = OpenAIProvider(settings, client=client_returning(200, body, seen))

    response = await provider.extract_structured(REQUEST)

    assert response.raw_json == '{"invoice_number": "A"}'
    assert response.model == "openai:gpt-x"
    assert response.usage.input_tokens == 10
    assert seen[0]["response_format"] == {"type": "json_object"}
    assert seen[0]["messages"][0] == {"role": "system", "content": "sys"}


async def test_openai_requires_api_key(settings: Settings) -> None:
    with pytest.raises(ProviderAuthError):
        OpenAIProvider(settings.model_copy(update={"openai_api_key": None}))


async def test_anthropic_forces_tool_and_reads_tool_input(settings: Settings) -> None:
    seen: list[dict[str, Any]] = []
    body = {
        "model": "claude-x",
        "content": [{"type": "tool_use", "input": {"invoice_number": "B"}}],
        "usage": {"input_tokens": 7, "output_tokens": 3},
    }
    provider = AnthropicProvider(settings, client=client_returning(200, body, seen))

    response = await provider.extract_structured(REQUEST)

    assert json.loads(response.raw_json) == {"invoice_number": "B"}
    assert seen[0]["tool_choice"]["type"] == "tool"
    assert seen[0]["tools"][0]["input_schema"] == {"type": "object"}


async def test_anthropic_without_tool_use_is_provider_error(settings: Settings) -> None:
    provider = AnthropicProvider(settings, client=client_returning(200, {"content": []}, []))

    with pytest.raises(ProviderError):
        await provider.extract_structured(REQUEST)


async def test_ollama_passes_schema_as_format(settings: Settings) -> None:
    seen: list[dict[str, Any]] = []
    body = {"model": "llama", "message": {"content": "{}"}, "prompt_eval_count": 4, "eval_count": 2}
    provider = OllamaProvider(settings, client=client_returning(200, body, seen))

    response = await provider.extract_structured(REQUEST)

    assert seen[0]["format"] == {"type": "object"}
    assert response.usage.output_tokens == 2


async def test_http_errors_are_mapped(settings: Settings) -> None:
    no_retry = settings.model_copy(update={"provider_max_retries": 0})

    with pytest.raises(ProviderRateLimitError):
        await OllamaProvider(no_retry, client=client_returning(429, {}, [])).extract_structured(
            REQUEST
        )
    with pytest.raises(ProviderAuthError):
        await OllamaProvider(no_retry, client=client_returning(401, {}, [])).extract_structured(
            REQUEST
        )
