FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT="/opt/venv" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

RUN uv venv /opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

RUN addgroup --system app && adduser --system --group app
RUN mkdir -p /app/assets && chown -R app:app /app/assets
USER app

ENTRYPOINT ["uvicorn", "main:app"]
CMD ["--host", "0.0.0.0", \
    "--port", "8000", \
    "--loop", "uvloop", \
    "--http", "httptools", \
    "--log-config", "log_conf.yaml"]
