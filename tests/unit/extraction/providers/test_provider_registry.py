import pytest

from docext.core.errors import UnknownProviderError
from docext.extraction.providers.registry import list_providers, resolve_model


def test_resolve_model_splits_provider_and_model() -> None:
    assert resolve_model("openai:gpt-4o-mini") == ("openai", "gpt-4o-mini")
    assert resolve_model("ollama:llama3.1:8b") == ("ollama", "llama3.1:8b")


@pytest.mark.parametrize("spec", ["gpt-4o", "openai:", ":x", "nope:model"])
def test_resolve_model_rejects_invalid(spec: str) -> None:
    with pytest.raises(UnknownProviderError):
        resolve_model(spec)


def test_list_providers_includes_mock() -> None:
    assert "mock" in list_providers()
