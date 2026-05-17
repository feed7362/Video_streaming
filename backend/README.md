# Backend (BFF)

Backend-For-Frontend in FastAPI. Single async service that owns auth, video metadata, comments, analytics, search, and the gateway for video file ingestion.

## Responsibilities

- REST API surface for the React frontend.
- Async I/O against PostgreSQL (asyncpg) and Elasticsearch (search).
- File uploads → MinIO (multipart) → publish encode job to RabbitMQ.
- Generates signed URLs consumed by the NGINX gateway for HLS streaming.
- Listens for `video.encode.status` and `video.failed` events from the convertor; updates DB + indexes documents in ES.
- Exposes `/api/metrics` (Prometheus) and `/api/health/{live,ready}`.

## Tech Stack

- **Framework**: FastAPI 0.129 + Uvicorn with `uvloop` + `httptools`.
- **ORM**: SQLAlchemy 2 async, Alembic for migrations.
- **Validation**: Pydantic v2.
- **Auth**: fastapi-users (JWT), httpx-oauth (GitHub).
- **Message queue**: faststream (RabbitMQ).
- **S3**: aiobotocore.
- **Cache / rate limiting**: redis-py async.
- **Search**: elasticsearch[async].
- **Secrets**: hvac (HashiCorp Vault).
- **Package manager**: uv.

## API Surface

| Router            | Purpose |
| ----------------- | ------- |
| `/api/auth`       | Register/login/me, password reset, GitHub OAuth, JWT issue |
| `/api/files`      | Multipart upload, signed URLs for MinIO HLS, download |
| `/api/videos`     | Video metadata CRUD, privacy toggle, by-category listings |
| `/api/comments`   | Per-video comments + replies + reactions; `/owner/list` for creator moderation |
| `/api/analytics`  | Creator dashboard (overview / content / audience) |
| `/api/search`     | Elasticsearch-backed search + autocomplete hints |
| `/api/health`     | `/live` (liveness), `/ready` (DB+S3+RMQ checks) |
| `/api/metrics`    | Prometheus exposition |

OpenAPI / Swagger UI at `/api/docs` when running.

## Configuration

All app config + secrets are loaded **from Vault** at startup via `src/config.py`. Vault mount paths: `secret/database`, `secret/s3`, `secret/jwt`, `secret/github_oauth`, `secret/redis`, `secret/rabbitmq`, `secret/elastic`.

Only two env vars are read directly: `VAULT_ADDR` and `VAULT_TOKEN`. Both set by Docker Compose / Helm.

### Required secrets

| Vault path              | Keys |
| ----------------------- | ---- |
| `secret/jwt`            | `JWT_SECRET` (≥32 chars — chart and Pydantic both fail-fast on shorter) |
| `secret/database`       | `POSTGRES_{HOST,PORT,DB,USER,PASSWORD}` |
| `secret/s3`             | `MINIO_*`, `BUCKET_NAMES` (comma-separated) |
| `secret/rabbitmq`       | `RABBITMQ_{HOST,PORT,USER,PASSWORD}` |
| `secret/elastic`        | `ELASTIC_{HOST,PASSWORD}` |
| `secret/redis`          | `REDIS_{HOST,PORT}` |
| `secret/github_oauth`   | `GITHUB_{CLIENT_ID,CLIENT_SECRET,CALLBACK_URL}`, `FRONTEND_URL` (all optional; empty disables OAuth flow) |

## Error envelope

All validation/handled errors return a consistent shape so the frontend can surface them via toast:

```json
{ "status": "error", "code": 400, "message": "Validation failed",
  "errors": [{ "loc": "body.name", "msg": "Field required", "type": "missing" }] }
```

See `app/exceptions.py`. The frontend `parseApiError` consumes this directly.

## Correlation IDs

`CorrelationIdMiddleware` (in `src/services/correlation.py`) reads `X-Request-ID` from the request or generates one, stores it in a contextvar, returns it on the response, and threads it into:
- Every log line via `RequestIdLogFilter` → `[rid=<uuid>]` in formatter.
- Outbound `broker.publish()` calls (headers + `correlation_id`) so the convertor logs share the same `rid`.

## Database migrations

Alembic in `alembic/`. Local:

```bash
uv run alembic revision --autogenerate -m "your message"
uv run alembic upgrade head
```

In Docker Compose, Alembic runs in-container at startup. In Kubernetes, the Helm chart runs migrations as a pre-install/pre-upgrade Job (`helm/templates/migrations-job.yaml`).

## Local development (without Docker)

```bash
uv sync
export VAULT_ADDR=http://localhost:8200 VAULT_TOKEN=<dev-token>
uv run uvicorn main:app --reload --log-config log_conf.yaml
```

## Testing

```bash
uv run pytest                     # unit tests (currently minimal coverage)
uv run pytest --cov=src --cov-report=term-missing
```

## Notable conventions

- Exception types are narrowed (no bare `except Exception:` in services/files.py, services/search.py, api/auth.py). Health checks intentionally keep `Exception` but log with `logging.exception` for traceability.
- All routes that mutate data require an authenticated user via `Depends(get_current_user_id)`.
- File uploads use inline `Form(...)` / `File(...)` params, **not** a Pydantic model via `Depends()` (FastAPI + Pydantic v2 quirk that silently treats Form fields as query params when bound through a model).
