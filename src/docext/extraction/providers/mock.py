"""Offline provider for tests and local development.

Models:
- `mock:echo`     → returns `{}` (every field null) — proves the pipeline wiring.
- `mock:fixture`  → returns `<settings.mock_fixture_dir>/<document_type>/<source stem>.json`.
- `mock:canned`   → returns the JSON given via `MockProvider.canned` (set by tests).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from docext.core.config import Settings
from docext.core.errors import ProviderError
from docext.extraction.providers.base import (
    ExtractionRequest,
    ModelProvider,
    ProviderCapabilities,
    ProviderResponse,
    Usage,
)


class MockProvider(ModelProvider):
    name = "mock"

    def __init__(self, settings: Settings, canned: dict[str, Any] | None = None) -> None:
        super().__init__(settings)
        self.canned = canned
        self.requests: list[ExtractionRequest] = []

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(vision=True, json_mode=True, max_context_tokens=1_000_000)

    async def extract_structured(self, request: ExtractionRequest) -> ProviderResponse:
        started = time.perf_counter()
        self.requests.append(request)
        payload: dict[str, Any]
        if request.model == "echo":
            payload = {}
        elif request.model == "canned":
            payload = self.canned or {}
        elif request.model == "fixture":
            payload = self._load_fixture(request)
        else:
            raise ProviderError(f"mock: unknown model '{request.model}'")
        return ProviderResponse(
            raw_json=json.dumps(payload),
            model=f"mock:{request.model}",
            usage=Usage(input_tokens=len(request.user_prompt) // 4, output_tokens=0),
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _load_fixture(self, request: ExtractionRequest) -> dict[str, Any]:
        if self.settings.mock_fixture_dir is None or not request.source_name:
            raise ProviderError("mock:fixture needs DOCEXT_MOCK_FIXTURE_DIR and a source filename")
        path = (
            Path(self.settings.mock_fixture_dir)
            / request.document_type
            / f"{Path(request.source_name).stem}.json"
        )
        if not path.exists():
            raise ProviderError(f"mock: fixture not found: {path}")
        data: dict[str, Any] = json.loads(path.read_text())
        return data
