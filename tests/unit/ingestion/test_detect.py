from docext.ingestion.detect import detect_mime


def test_detect_pdf_by_magic_regardless_of_extension() -> None:
    assert detect_mime(b"%PDF-1.7 ...", "whatever.bin") == "application/pdf"


def test_detect_unknown_falls_back_to_octet_stream() -> None:
    assert detect_mime(b"hello", "x.pdf") == "application/octet-stream"
