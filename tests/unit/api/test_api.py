from fastapi.testclient import TestClient
from tests.conftest import make_pdf

from docext.api.app import create_app


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


def test_extract_endpoint_maps_domain_errors() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/v1/extract",
        files={"file": ("x.pdf", make_pdf(["x"]), "application/pdf")},
        data={"type": "unknown_type", "model": "mock:echo"},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unknown_document_type"
