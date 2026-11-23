FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Run the project's virtualenv directly; `uv run` would re-sync (including dev deps) at start-up
    PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home appuser

# Install dependencies first for optimal Docker layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy application code and collect static files.
# collectstatic only needs importable settings, so a throwaway key is fine here.
COPY --chown=appuser:appuser . .
RUN uv sync --locked --no-dev && \
    DJANGO_SECRET_KEY=build-only-not-secret python manage.py collectstatic --noinput && \
    mkdir -p /app/data && chown -R appuser:appuser /app/data /app/staticfiles

USER appuser

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
