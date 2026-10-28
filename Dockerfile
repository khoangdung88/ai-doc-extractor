# syntax=docker/dockerfile:1
# docext — one-command container: `docker build -t docext . && docker run -p 8000:8000 docext`

# ---- build stage: resolve locked deps + install the project -------------------
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

# ---- runtime stage: slim image, venv only, non-root ----------------------------
FROM python:3.11-slim-bookworm AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    DOCEXT_ENV=prod \
    # Default: reach Ollama on the Docker host (Docker Desktop, Win/Mac). Override with -e.
    OLLAMA_BASE_URL=http://host.docker.internal:11434

WORKDIR /app
RUN useradd --create-home appuser
COPY --from=builder /app/.venv ./.venv
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"]

# API + web UI on :8000. Secrets come from `docker run -e/--env-file`, never the image.
CMD ["uvicorn", "docext.api.app:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
