"""MIME detection by content sniffing (never trust the file extension alone)."""

from __future__ import annotations

_MAGIC: tuple[tuple[bytes, str], ...] = (
    (b"%PDF-", "application/pdf"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"PK\x03\x04", "application/zip"),
)


def detect_mime(data: bytes, filename: str | None = None) -> str:
    head = data[:16]
    for magic, mime in _MAGIC:
        if head.startswith(magic):
            return mime
    if filename and filename.lower().endswith(".txt"):
        return "text/plain"
    return "application/octet-stream"
