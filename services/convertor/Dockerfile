FROM jrottenberg/ffmpeg:7.1-nvidia2204

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3.10  \
    python3-pip  \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV PATH="/opt/venv/bin:${PATH}" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT="/opt/venv"

RUN uv venv /opt/venv

COPY pyproject.toml ./

RUN uv sync --no-dev

COPY . .

ENTRYPOINT ["python3", "-m", "uvicorn", "rabbit_client:app", "--host", "0.0.0.0", "--port", "8002","--loop", "uvloop", "--http", "httptools", "--workers", "4", "--log-config", "log_conf.yaml"]
