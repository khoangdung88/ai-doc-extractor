from docext.core.errors import DocextError, ProviderRateLimitError, UnknownDocumentTypeError


def test_errors_carry_stable_code_and_status() -> None:
    err = UnknownDocumentTypeError("x", details={"available": ["invoice"]})

    assert isinstance(err, DocextError)
    assert err.code == "unknown_document_type"
    assert err.http_status == 400
    assert err.details == {"available": ["invoice"]}


def test_rate_limit_is_a_provider_error_with_429() -> None:
    assert ProviderRateLimitError("x").http_status == 429
