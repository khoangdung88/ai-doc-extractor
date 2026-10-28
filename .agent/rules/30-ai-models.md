# 30 — AI model usage rules

## Provider abstraction
- All model access goes through `ModelProvider` (`extraction/providers/base.py`). SDK imports happen only
  inside the provider module and lazily (`import openai` inside `__init__`/method), so the core package
  installs without any vendor SDK.
- A model is addressed as `"<provider>:<model_name>"` (e.g. `openai:gpt-4o-mini`, `ollama:llama3.1`).
  Parsing happens once, in `providers/registry.py::resolve_model`.
- Providers implement `extract_structured(request: ExtractionRequest) -> ProviderResponse` returning
  **raw JSON text + usage + latency**. Validation against the schema happens in the pipeline, not in the
  provider, so every provider is validated identically.
- Prefer each vendor's native structured output / JSON mode when available; fall back to prompt-based JSON
  + repair. Document which mode a provider uses in its module docstring.
- Every provider supports: text input; optional page images (for vision-capable models, flag
  `capabilities.vision`); timeout; max retries with exponential backoff on 429/5xx only.

## Prompts
- Prompts are files in `src/docext/extraction/prompts/<doc_type>/<version>.md`, not inline strings.
  They are rendered with a tiny templating step (`prompts/loader.py`). Changing a prompt = new version file;
  old versions stay until no tests reference them.
- A prompt consists of: role, task, the JSON schema (auto-generated from the Pydantic model, never
  hand-written), field-by-field extraction rules, and output constraints. Keep it deterministic:
  temperature 0 unless an ADR says otherwise.
- Do not put example documents containing real company data in prompts.

## Determinism, cost, observability
- Every `ExtractionResult` carries `model`, `prompt_version`, `usage` (tokens), `latency_ms`,
  `confidence` (if the model provides it), and `warnings`.
- Budget guard: the pipeline refuses inputs over `settings.max_input_tokens` with a typed error instead of
  silently truncating. Truncation strategies are explicit features with specs.
- Log one `extraction_completed` / `extraction_failed` event per call with model, doc_type, tokens, ms.

## Testing models
- Unit tests use `mock:echo` / `mock:fixture` providers only. Never hit a real API in unit tests.
- Integration tests (`tests/integration`, marker `integration`) run only when the provider's key is present
  and are excluded from default CI. Golden outputs live in `tests/fixtures/golden/<doc_type>/`.
- When evaluating a new model or prompt, record the comparison in `docs/evals/` (date, model, prompt
  version, fixture set, field-level accuracy). Never claim "better" without numbers.
