FROM jrottenberg/ffmpeg:7.1-nvidia2204

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_PROJECT_ENVIRONMENT="/opt/venv" \
    UV_PYTHON_INSTALL_DIR="/opt/python"\
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:$PATH"

RUN uv venv /opt/venv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

COPY . .

RUN addgroup --system app && adduser --system --group app
USER app

ENTRYPOINT ["uvicorn", "rabbit_client:app"]
CMD ["--host", "0.0.0.0", \
    "--port", "9102", \
    "--loop", "uvloop", \
    "--http", "httptools", \
    "--log-config", "log_conf.yaml"]
