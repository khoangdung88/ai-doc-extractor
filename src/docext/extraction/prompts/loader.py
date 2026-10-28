"""Load and render prompt files. Sections `## System` and `## Task` become the two message roles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_PROMPTS_DIR = Path(__file__).parent
_SECTION = re.compile(r"^## (System|Task)\s*$", re.MULTILINE)
_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    document_type: str
    version: str
    system: str
    task: str

    def render(self, **variables: str) -> tuple[str, str]:
        return _render(self.system, variables), _render(self.task, variables)


def _render(text: str, variables: dict[str, str]) -> str:
    def sub(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"prompt variable '{key}' not provided")
        return variables[key]

    return re.sub(r"\{\{\s*(\w+)\s*\}\}", sub, text)


@lru_cache(maxsize=64)
def load_prompt(document_type: str, version: str) -> PromptTemplate:
    path = _PROMPTS_DIR / document_type / f"{version}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    raw = _COMMENT.sub("", path.read_text(encoding="utf-8"))
    parts = _SECTION.split(raw)
    sections = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    if "System" not in sections or "Task" not in sections:
        raise ValueError(f"Prompt {path} must contain '## System' and '## Task' sections")
    return PromptTemplate(document_type, version, sections["System"], sections["Task"])
