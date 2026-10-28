"""Typed exceptions. Every error raised by docext derives from `DocextError`."""

from __future__ import annotations


class DocextError(Exception):
    """Base error. `code` is stable and machine-readable; `http_status` hints the API layer."""

    code = "internal_error"
    http_status = 500

    def __init__(self, message: str, *, details: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


# --- input / ingestion -------------------------------------------------------
class InputTooLargeError(DocextError):
    code = "input_too_large"
    http_status = 413


class UnsupportedFormatError(DocextError):
    code = "unsupported_format"
    http_status = 415


class DocumentLoadError(DocextError):
    code = "document_load_failed"
    http_status = 422


class EncryptedDocumentError(DocumentLoadError):
    code = "document_encrypted"


# --- domain -------------------------------------------------------------------
class UnknownDocumentTypeError(DocextError):
    code = "unknown_document_type"
    http_status = 400


# --- providers ----------------------------------------------------------------
class UnknownProviderError(DocextError):
    code = "unknown_provider"
    http_status = 400


class ProviderNotInstalledError(DocextError):
    code = "provider_not_installed"
    http_status = 501


class ProviderError(DocextError):
    code = "provider_error"
    http_status = 502


class ProviderAuthError(ProviderError):
    code = "provider_auth_failed"
    http_status = 500


class ProviderRateLimitError(ProviderError):
    code = "provider_rate_limited"
    http_status = 429


class ProviderTimeoutError(ProviderError):
    code = "provider_timeout"
    http_status = 504


# --- extraction ---------------------------------------------------------------
class ExtractionValidationError(DocextError):
    """The model returned output that does not conform to the document schema."""

    code = "extraction_validation_failed"
    http_status = 502
