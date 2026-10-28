"""Extraction layer: pipeline + prompts + model providers.

Add a provider via `.agent/workflows/new-model-provider.md`.
"""

from docext.extraction.pipeline import ExtractionResult, extract

__all__ = ["ExtractionResult", "extract"]
