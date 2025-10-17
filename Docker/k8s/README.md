# Kubernetes Manifests for Video Streaming Stack

This directory contains Kubernetes resources that mirror the services defined in `Docker/docker-compose.yml`.

## Contents

- Namespace and shared service account for Vault agent injection.
- ConfigMaps for nginx, Vault, and monitoring stack configurations.
- A PersistentVolumeClaim dedicated to the PostgreSQL database.
- Deployments and Services for every application component (backend, frontend, media processing, storage, messaging, monitoring, and Vault).

## Vault integration

All Deployments use the Vault Agent Injector to retrieve sensitive configuration. The following secrets (stored in Vault's KV store) are expected:

| Service | Vault path | Expected keys |
|---------|------------|---------------|
| Backend API | `secret/data/backend/database` | `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` |
| Backend API | `secret/data/backend/s3` | `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_ENDPOINT_URL`, `MINIO_REGION_NAME` |
| PostgreSQL | `secret/data/postgres` | `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, optional connection overrides |
| MinIO | `secret/data/minio` | `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `MINIO_ENDPOINT_URL`, etc. |
| Grafana | `secret/data/grafana` | `GF_SECURITY_ADMIN_USER`, `GF_SECURITY_ADMIN_PASSWORD`, `GF_USERS_ALLOW_SIGN_UP`, `GF_SERVER_SERVE_FROM_SUB_PATH`, `GF_SERVER_ROOT_URL` |

Ensure the Vault role `video-streaming` grants read access to these paths for the `vault-auth` service account.

## Applying the manifests

```bash
kubectl apply -f namespace.yaml
kubectl apply -f configmap-gateway.yaml -f configmap-vault.yaml -f configmap-monitoring.yaml
kubectl apply -f postgres-pvc.yaml
kubectl apply -f deployment-*.yaml
```

Apply additional storage classes or adjust resource requests as required by your cluster.
