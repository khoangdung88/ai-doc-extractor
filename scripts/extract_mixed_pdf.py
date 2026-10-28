"""Extract several document types from ONE combined PDF by page ranges (no file splitting).

The pipeline is 1 file → 1 document type; this helper loads the PDF once, slices
`Document.pages` per mapping and runs the real extraction pipeline per type.

Run:
    .venv\\Scripts\\python.exe scripts/extract_mixed_pdf.py combined.pdf \
        invoice:1 packing_list:2 --model mock:echo

Page specs: `invoice:1`, `packing_list:2-4`, `booking_confirmation:1,3`.
Output: one JSON object `{ "<type>": <ExtractionResult>, ... }` on stdout,
or one file per type with `--out-dir`.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

from docext.core.config import get_settings
from docext.domain.registry import get_document_type
from docext.extraction.pipeline import ExtractionResult, extract
from docext.extraction.providers.registry import create_provider, resolve_model
from docext.ingestion.base import Document
from docext.ingestion.registry import load_document


def parse_mapping(arg: str, page_count: int) -> tuple[str, list[int]]:
    doc_type, sep, spec = arg.partition(":")
    if not sep or not doc_type or not spec:
        raise ValueError(f"Mapping must be '<document_type>:<pages>', got '{arg}'")
    get_document_type(doc_type)
    pages: set[int] = set()
    for part in spec.split(","):
        start, _, end = part.partition("-")
        if end:
            pages.update(range(int(start), int(end) + 1))
        else:
            pages.add(int(start))
    ordered = sorted(pages)
    if ordered[0] < 1 or ordered[-1] > page_count:
        raise ValueError(
            f"Pages {ordered} out of range for '{arg}' (document has {page_count} pages)"
        )
    return doc_type, ordered


async def run(
    pdf_path: Path, mappings: list[str], model: str | None
) -> dict[str, ExtractionResult]:
    settings = get_settings()
    document = await load_document(pdf_path.read_bytes(), pdf_path.name, settings=settings)
    spec = model or settings.default_model
    provider = create_provider(resolve_model(spec)[0], settings)
    results: dict[str, ExtractionResult] = {}
    try:
        for arg in mappings:
            doc_type, page_numbers = parse_mapping(arg, len(document.pages))
            sub_document = Document(
                filename=document.filename,
                mime_type=document.mime_type,
                pages=[p for p in document.pages if p.number in page_numbers],
                metadata=dict(document.metadata),
            )
            results[doc_type] = await extract(
                sub_document, doc_type, spec, settings=settings, provider=provider
            )
    finally:
        await provider.close()
    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("pdf", type=Path, help="Combined PDF file")
    parser.add_argument(
        "mappings",
        nargs="+",
        help="'<document_type>:<pages>', e.g. invoice:1 packing_list:2-3",
    )
    parser.add_argument(
        "--model", default=None, help="<provider>:<model> (default: DOCEXT_DEFAULT_MODEL)"
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Write one <type>.json per result instead of stdout",
    )
    args = parser.parse_args()

    try:
        results = asyncio.run(run(args.pdf, args.mappings, args.model))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.out_dir:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        for doc_type, result in results.items():
            (args.out_dir / f"{doc_type}.json").write_text(result.model_dump_json(indent=2))
        print(f"wrote {len(results)} file(s) to {args.out_dir}")
    else:
        print(json.dumps({k: v.model_dump(mode="json") for k, v in results.items()}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
