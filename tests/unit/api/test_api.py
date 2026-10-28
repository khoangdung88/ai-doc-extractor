from fastapi.testclient import TestClient
from tests.conftest import make_pdf

from docext.api.app import create_app
from docext.extraction.providers.base import ProviderResponse
from docext.extraction.providers.mock import MockProvider


def test_health_and_discovery_endpoints() -> None:
    client = TestClient(create_app())

    assert client.get("/health").json()["status"] == "ok"
    assert {t["name"] for t in client.get("/v1/document-types").json()} >= {"invoice"}
    assert "mock" in client.get("/v1/providers").json()


def test_extract_endpoint_with_pdf_and_mock_model() -> None:
    client = TestClient(create_app())
    pdf = make_pdf(["PACKING LIST", "CTN 1-10 Net 100 KG"])

    response = client.post(
        "/v1/extract",
        files={"file": ("pl.pdf", pdf, "application/pdf")},
        data={"type": "packing_list", "model": "mock:echo"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["document_type"] == "packing_list"
    assert body["data"]["packages"] == []


def test_extract_endpoint_without_type_auto_detects() -> None:
    client = TestClient(create_app())
    pdf = make_pdf(["PACKING LIST", "CTN 1-10 Net 100 KG"])

    response = client.post(
        "/v1/extract",
        files={"file": ("combined.pdf", pdf, "application/pdf")},
        data={"model": "mock:echo"},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    # mock:echo returns no labels -> every page is reported as skipped
    assert body["results"] == []
    assert body["skipped_pages"][0]["pages"] == [1]


def test_ui_index_and_config_endpoint() -> None:
    client = TestClient(create_app())

    index = client.get("/")
    assert index.status_code == 200
    assert "docext" in index.text

    config = client.get("/v1/config").json()
    assert config["default_model"] == "mock:echo"
    flags = {p["name"]: p["requires_api_key"] for p in config["providers"]}
    assert flags["openai"] and flags["anthropic"]
    assert not flags["mock"] and not flags["ollama"]


def test_provider_models_endpoint() -> None:
    client = TestClient(create_app())

    assert client.get("/v1/models", params={"provider": "mock"}).json()["models"] == []

    unknown = client.get("/v1/models", params={"provider": "nope"})
    assert unknown.status_code == 400
    assert unknown.json()["error"]["code"] == "unknown_provider"


def test_extract_api_key_override_reaches_provider(monkeypatch) -> None:
    captured = {}

    class _ProbeProvider(MockProvider):
        def __init__(self, settings) -> None:  # type: ignore[no-untyped-def]
            super().__init__(settings)
            captured["openai_api_key"] = settings.openai_api_key

        async def extract_structured(self, request):  # type: ignore[no-untyped-def]
            return ProviderResponse(raw_json="{}", model="probe")

    monkeypatch.setattr(
        "docext.extraction.pipeline.create_provider",
        lambda name, settings: _ProbeProvider(settings),
    )
    client = TestClient(create_app())

    response = client.post(
        "/v1/extract",
        files={"file": ("x.pdf", make_pdf(["INVOICE"]), "application/pdf")},
        data={"type": "invoice", "model": "openai:gpt-4o-mini", "api_key": "sk-test-123"},
    )

    assert response.status_code == 200, response.text
    assert captured["openai_api_key"] == "sk-test-123"


def test_extract_api_key_ignored_for_keyless_provider() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/extract",
        files={"file": ("x.pdf", make_pdf(["INVOICE"]), "application/pdf")},
        data={"type": "invoice", "model": "mock:echo", "api_key": "ignored"},
    )

    assert response.status_code == 200, response.text


def test_preview_returns_page_text() -> None:
    client = TestClient(create_app())
    pdf = make_pdf(["PACKING LIST", "CTN 1-10 Net 100 KG"])

    response = client.post(
        "/v1/preview",
        files={"file": ("pl.pdf", pdf, "application/pdf")},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["mime_type"] == "application/pdf"
    assert body["pages"] == [{"number": 1, "text": "PACKING LIST\nCTN 1-10 Net 100 KG\n"}]


def test_preview_rejects_non_pdf() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/preview",
        files={"file": ("x.bin", b"not a pdf", "application/octet-stream")},
    )

    assert response.status_code == 415
    assert response.json()["error"]["code"] == "unsupported_format"


def test_extract_endpoint_maps_domain_errors() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/extract",
        files={"file": ("x.pdf", make_pdf(["x"]), "application/pdf")},
        data={"type": "unknown_type", "model": "mock:echo"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_document_type"
