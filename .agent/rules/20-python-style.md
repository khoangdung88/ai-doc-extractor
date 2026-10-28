# 20 — Python style

- Python 3.11+. Tooling: `uv`, `ruff` (lint+format, line length 100), `mypy --strict`.
- Full type hints on every function, including tests' helpers. `Any` requires a comment explaining why.
- Prefer `pydantic.BaseModel` for data crossing boundaries, `@dataclass(frozen=True, slots=True)` for
  internal value objects, plain functions over classes when there is no state.
- Module layout: imports → constants → public API → private helpers. One concept per module; if a file passes
  ~300 lines, split it.
- Naming: `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE` constants. Names say *what*,
  not *how*. No abbreviations beyond the glossary (`bl`, `hs_code`, `pol`, `pod` are allowed — see
  `context/glossary.md`).
- Docstrings: every public module, class, and function gets a one-line summary; longer only when
  behavior is non-obvious. No docstrings that restate the signature.
- Comments explain *why*, never *what*. No commented-out code. `TODO(#issue):` only with an issue number.
- Logging: `structlog` via `core.logging.get_logger(__name__)`. Log events as `snake_case` nouns with
  key/value context (`log.info("extraction_completed", doc_type=..., model=..., ms=...)`). Never log document
  content or secrets.
- Errors: see `10-architecture.md#errors`. Add new exception classes to `core/errors.py` only.
- Imports: absolute (`from docext.domain import ...`). No wildcard imports. No imports inside functions
  except to break genuine cycles or for optional heavy SDKs inside providers.
- Datetime: always timezone-aware UTC. Money: `Decimal`, never `float`. Store currency as ISO-4217 code.
