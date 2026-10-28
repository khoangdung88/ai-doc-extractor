"""Tolerant parsing of model output into a JSON object (model output is untrusted input)."""

from __future__ import annotations

import json
import re
from typing import Any

from docext.core.errors import ExtractionValidationError

_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def parse_json_output(text: str) -> dict[str, Any]:
    cleaned = _FENCE.sub("", text.strip()).strip()
    candidates = [cleaned]
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end > start:
        candidates.append(cleaned[start : end + 1])
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    raise ExtractionValidationError(
        "Model output is not a JSON object", details={"preview": text[:200]}
    )
