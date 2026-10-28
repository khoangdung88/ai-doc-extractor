"""Typer CLI mirroring the API. Thin adapter: no business logic."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from docext.core.config import get_settings
from docext.core.errors import DocextError
from docext.core.logging import configure_logging

app = typer.Typer(help="docext — AI extraction for shipping documents.", no_args_is_help=True)


@app.callback()
def _init(verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False) -> None:
    configure_logging("DEBUG" if verbose else get_settings().log_level)


@app.command()
def extract(
    path: Annotated[Path, typer.Argument(exists=True, readable=True, help="Document file")],
    type: Annotated[str, typer.Option("--type", "-t", help="invoice | packing_list | ...")],
    model: Annotated[str | None, typer.Option("--model", "-m", help="<provider>:<model>")] = None,
    output: Annotated[Path | None, typer.Option("--output", "-o", help="Write JSON here")] = None,
) -> None:
    """Extract structured data from one document."""
    from docext.extraction.pipeline import extract as run_extraction
    from docext.ingestion.registry import load_document

    async def _run() -> str:
        document = await load_document(path.read_bytes(), path.name)
        result = await run_extraction(document, type, model)
        return result.model_dump_json(indent=2)

    try:
        text = asyncio.run(_run())
    except DocextError as exc:
        typer.secho(f"error [{exc.code}]: {exc.message}", fg=typer.colors.RED, err=True)
        if exc.details:
            typer.echo(json.dumps(exc.details, indent=2, default=str), err=True)
        raise typer.Exit(code=1) from None
    if output:
        output.write_text(text)
        typer.echo(f"wrote {output}", err=True)
    else:
        sys.stdout.write(text + "\n")


@app.command()
def types() -> None:
    """List registered document types."""
    from docext.domain.registry import list_document_types

    for t in list_document_types():
        typer.echo(f"{t.name:24} {t.title} (prompt {t.prompt_version})")


@app.command()
def providers() -> None:
    """List registered model providers."""
    from docext.extraction.providers.registry import list_providers

    for name in list_providers():
        typer.echo(name)


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
) -> None:
    """Run the HTTP API."""
    import uvicorn

    uvicorn.run("docext.api.app:create_app", factory=True, host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
