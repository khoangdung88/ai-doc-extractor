# Workflow — Add a new input format (image, xlsx, docx, email, ...)

1. **Spec** in `docs/features/NNNN-input-<format>.md`: MIME types, how text/pages are produced
   (native text vs OCR vs render-to-image for vision models), size limits, failure modes.
2. **ADR** for any new dependency (OCR engines are heavy — justify).
3. **Implementation**: `src/docext/ingestion/<format>.py` with `<Format>Loader(Loader)`:
   `supports(mime, filename) -> bool`, `async load(source) -> Document`. Output must fill
   `Document.pages[*].text` and, if the format is visual, `Document.pages[*].image_png` for vision models.
4. **Register** in `ingestion/registry.py`; MIME sniffing by content in `ingestion/detect.py`.
5. **Fixtures + tests**: at least 2 synthetic files, loader unit tests, one pipeline golden test.
6. **Docs**: README supported formats, `docs/architecture.md`, CHANGELOG.
7. **PR** `feat(ingestion): add <format> loader`.
