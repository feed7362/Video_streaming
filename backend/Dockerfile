# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# OS deps in one layer with cache mount for apt
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT="/opt/venv" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app"

RUN uv venv /opt/venv

# Lockfile first — this layer only changes when deps change
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev --frozen

# Source — only this layer rebuilds on code changes
COPY src ./src
COPY app ./app
COPY main.py log_conf.yaml alembic.ini ./
COPY alembic ./alembic
COPY utils ./utils

RUN addgroup --system app && adduser --system --group --home /app app \
    && chown -R app:app /app /opt/venv
USER app

ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", \
    "--port", "8000", \
    "--loop", "uvloop", \
    "--http", "httptools", \
    "--log-config", "log_conf.yaml"]
