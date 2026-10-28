# 60 — Security & data handling

- Secrets only via environment / `.env` (git-ignored). `.env.example` lists keys with empty values.
  Never print, log, or commit a key. CI secrets are GitHub Actions secrets.
- Documents can contain personal and commercially sensitive data (names, addresses, prices, bank accounts).
  - Never commit real customer documents. Fixtures are synthetic or thoroughly anonymised.
  - Never log document text or extracted values at INFO level; DEBUG may log lengths/hashes only.
  - Uploaded files are processed in memory or in a temp dir that is deleted after the request.
- Treat model output as untrusted input: validate with Pydantic, never `eval`, never pass it to a shell or SQL.
- Prompt injection: document text goes into the user turn, never the system prompt; instructions in the
  document are ignored by design — add a test when touching prompt assembly.
- Dependencies: pin with upper bounds in `pyproject.toml`, lockfile committed, Dependabot enabled. Adding a
  dependency requires justification in the PR and, for core deps, an ADR.
- File handling: enforce `settings.max_upload_mb`, check MIME/type by content not extension, reject
  encrypted PDFs with a typed error.
