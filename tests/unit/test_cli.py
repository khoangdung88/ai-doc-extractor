from pathlib import Path

from tests.conftest import make_pdf
from typer.testing import CliRunner

from docext.cli import app

runner = CliRunner()


def test_cli_lists_types_and_providers() -> None:
    assert "invoice" in runner.invoke(app, ["types"]).output
    assert "mock" in runner.invoke(app, ["providers"]).output


def test_cli_extract_writes_json(tmp_path: Path) -> None:
    pdf = tmp_path / "inv.pdf"
    pdf.write_bytes(make_pdf(["INVOICE INV-9"]))

    result = runner.invoke(app, ["extract", str(pdf), "--type", "invoice", "--model", "mock:echo"])

    assert result.exit_code == 0, result.output
    assert '"document_type": "invoice"' in result.output


def test_cli_extract_without_type_auto_detects(tmp_path: Path) -> None:
    pdf = tmp_path / "combined.pdf"
    pdf.write_bytes(make_pdf(["INVOICE INV-9"]))

    result = runner.invoke(app, ["extract", str(pdf), "--model", "mock:echo"])

    assert result.exit_code == 0, result.output
    assert '"results"' in result.output
    assert '"skipped_pages"' in result.output
