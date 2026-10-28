"""Shared httpx helpers for REST-based providers: timeout, retry on 429/5xx, error mapping."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from docext.core.config import Settings
from docext.core.errors import (
    ProviderAuthError,
    ProviderError,
    ProviderRateLimitError,
    ProviderTimeoutError,
)

_RETRY_STATUSES = {429, 500, 502, 503, 504}


def make_client(settings: Settings, base_url: str, headers: dict[str, str]) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=base_url, headers=headers, timeout=httpx.Timeout(settings.provider_timeout_s)
    )


async def post_json(
    client: httpx.AsyncClient,
    path: str,
    payload: dict[str, Any],
    *,
    max_retries: int,
    provider: str,
) -> dict[str, Any]:
    attempt = 0
    while True:
        try:
            response = await client.post(path, json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError(f"{provider}: request timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderError(f"{provider}: transport error: {exc}") from exc

        if response.status_code in _RETRY_STATUSES and attempt < max_retries:
            attempt += 1
            await asyncio.sleep(min(2**attempt, 10))
            continue
        if response.status_code in (401, 403):
            raise ProviderAuthError(f"{provider}: authentication failed")
        if response.status_code == 429:
            raise ProviderRateLimitError(f"{provider}: rate limited")
        if response.status_code >= 400:
            raise ProviderError(
                f"{provider}: HTTP {response.status_code}",
                details={"body": response.text[:500]},
            )
        body: dict[str, Any] = response.json()
        return body
