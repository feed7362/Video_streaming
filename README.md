# Video Streaming Platform

Microservice video platform: FastAPI backend, React/Vite frontend, FFmpeg/NVENC encoder, MinIO storage, RabbitMQ, PostgreSQL, Elasticsearch, Redis, Vault, observability stack. One-command bring-up via Docker Compose; optional Helm chart for Kubernetes.

## ✨ Features

- **Microservices**: decoupled bff / frontend / convertor / moderation.
- **Async backend**: FastAPI + asyncpg + aiobotocore + faststream. Vault for secrets.
- **Modern frontend**: React 19, Vite, TypeScript strict, shadcn/ui, Tailwind v4, HLS.js, react-hook-form + Zod, sonner toasts.
- **Async encoding**: RabbitMQ-fed FFmpeg with NVENC + CPU fallback; dead-letter queue + bounded retries.
- **Observability**: Prometheus + Loki + Promtail + Grafana + Alertmanager. Per-request correlation IDs threaded BFF → RabbitMQ → convertor.
- **Robust CI/CD**: GitHub Actions, pre-commit (black/ruff/mypy/eslint/prettier/gitleaks/bandit), Dependabot.
- **Containerized**: Docker Compose for dev/staging, Helm chart for Kubernetes, Buildx Bake for fast parallel builds.

## 🏛️ Architecture

```
            ┌──────────────┐
            │  NGINX (GW)  │ ← single entrypoint at :80
            └──────┬───────┘
   ┌──────────────┼─────────────────┬─────────────┐
   ▼              ▼                 ▼             ▼
 React          FastAPI BFF       MinIO         Grafana
 (Vite)         │                  (S3)         /Prometheus
                ├─ PostgreSQL                   /Loki/AM
                ├─ Redis  (cache/rate-limit)
                ├─ Elasticsearch (search)
                ├─ Vault  (secrets, auto-unsealed by sidecar)
                └─ RabbitMQ ─► Convertor (NVENC → HLS)
                                       ↓ on failure
                                  video.dlx → video.encode.dlq
                                  video.failed (terminal)
```

## 🛠️ Tech Stack

| Category      | Technologies |
| :------------ | :----------- |
| Backend       | Python 3.12, FastAPI, SQLAlchemy 2 async, asyncpg, Pydantic v2, fastapi-users, faststream, aiobotocore, hvac, prometheus-client |
| Frontend      | React 19, Vite, TypeScript strict, shadcn/ui (Radix + Tailwind v4), HLS.js, Axios, react-hook-form + Zod, sonner |
| Database      | PostgreSQL, Alembic |
| Services      | RabbitMQ, FFmpeg (NVENC) |
| Storage       | MinIO (S3-compatible) |
| Secrets       | HashiCorp Vault + sidecar auto-unsealer |
| DevOps        | Docker, Docker Compose, Buildx Bake, Helm (chart in `helm/`), GitHub Actions, NGINX, Pre-commit, Gitleaks, Bandit, Dependabot |
| Observability | Prometheus, Alertmanager, Grafana, Loki, Promtail |

## 🚀 Getting Started

### Prerequisites
- Docker + Docker Compose v2.
- NVIDIA GPU + Container Toolkit for the convertor (CPU-only fallback works but is slow).

### Quick start

```bash
git clone <repo-url> && cd <repo>

# 1. Configure env. Copy and fill the example.
cp Docker/.env.example Docker/.env
# Required at minimum: VAULT_TOKEN, POSTGRES_*, MINIO_*, ELASTIC_PASSWORD,
# CLUSTER_NAME, LICENSE, GRAFANA_ADMIN_USER, GRAFANA_ADMIN_PASSWORD.

# 2. Vault unseal keys (first install only).
cp vault/unseal-keys.env.example vault/unseal-keys.env
# After `vault operator init` paste 3 of 5 keys into this file.

# 3. Bring everything up. Compose project name is set in the file —
# no `-p` flag needed.
docker compose -f ./Docker/docker-compose.yml up -d --build
```

### Endpoints (default ports via gateway)

| Service        | URL |
| -------------- | --- |
| Frontend       | `http://localhost` |
| Backend docs   | `http://localhost/api/docs` |
| Grafana        | `http://localhost/grafana` (creds from `.env`) |
| Prometheus     | `http://localhost/prometheus/` |
| Alertmanager   | exposed in-cluster only; reach via `docker exec alertmanager wget -qO- http://localhost:9093/api/v2/status` |
| MinIO Console  | `http://localhost/minio/ui` |
| RabbitMQ       | `http://localhost/rabbitmq` |
| Vault UI       | `http://localhost/ui/` |

## ⚡ Fast builds with Buildx Bake

For iterative development the included `docker-bake.hcl` builds bff + frontend + convertor in parallel with shared BuildKit cache:

```bash
# one-time builder setup
docker buildx create --name vsbuilder --driver docker-container --bootstrap
docker buildx use vsbuilder

# build everything in parallel
docker buildx bake

# only the lighter targets
docker buildx bake app

# bring up using the freshly-baked images (no rebuild)
docker compose -f ./Docker/docker-compose.yml up -d --no-build
```

First clean build is ~2–3 min. Incremental builds after a single source change drop to ~5–10 s thanks to `--mount=type=cache` for uv/npm and a local layer cache in `.buildx-cache/`.

## ☸️ Kubernetes / Helm

Production-shaped Helm chart lives in `helm/`. It includes ConfigMap, Secret with `JWT_SECRET ≥ 32 char` fail-fast, ServiceAccount, per-service Deployment/Service with probes + resource limits + non-root security context, HPA, PDB, ingress, and an Alembic migration Job (pre-install/upgrade hook). Sub-charts bundle PostgreSQL, MinIO, RabbitMQ, Vault, Prometheus, Alertmanager, Grafana, Loki, Promtail.

```bash
cd helm
helm dependency update
helm install dev . --namespace video --create-namespace \
  --set 'secret.data.JWT_SECRET=long-random-32+-char-secret-please'
```

See `helm/values.yaml` for the full configuration surface.

## 🔒 Secrets management

- **Application secrets** live in Vault. The BFF loads them via `hvac` at startup (`src/config.py`). Vault auto-unseals on every boot via a tiny `curlimages/curl` sidecar that posts unseal keys from a gitignored `vault/unseal-keys.env`.
- **JWT_SECRET** is required and fail-fast: min 32 chars or BFF aborts. No more `CHANGE-ME-IN-PRODUCTION` default.
- **Grafana admin** is no longer `admin/admin`. Set `GRAFANA_ADMIN_PASSWORD` in `Docker/.env`; compose refuses to start without it.
- **Frontend API base URL** defaults to same-origin (`""`). Override only when running `vite dev` directly via `VITE_API_BASE_URL`.

## 🔍 Observability and tracing

Every HTTP request gets an `X-Request-ID` (generated if absent, accepted if present). It propagates through:
- BFF logs (`[rid=…]` formatter via a logging Filter).
- RabbitMQ message headers + `correlation_id`.
- Convertor logs after each message consume.

To trace a single request across services:
```bash
curl -H "X-Request-ID: trace-demo" http://localhost/api/videos/?page=1
docker logs bff_service 2>&1 | grep trace-demo
docker logs ffmpeg_service 2>&1 | grep trace-demo
```

Alertmanager rules in `monitoring/alert.rules.yml` cover ServiceDown, 5xx-rate, p95 latency, ConvertorDown, ProcessRestartLoop.

## 🤝 Contributing

1. Fork the repo.
2. `pre-commit install` to enable hooks.
3. Make changes; commit (hooks reformat with black/ruff/prettier).
4. Open a PR using the templates in `.github/`.

## 📄 License

Apache License 2.0 — see [LICENSE](LICENSE).
