# Helm chart — `video-streaming`

Deploys the full stack to Kubernetes: bff + frontend + convertor + their dependencies (Postgres, MinIO, RabbitMQ, Vault, Prometheus + Alertmanager, Grafana, Loki, Promtail).

> **Maturity**: usable for dev/staging; production needs the secret-store integration described below.

## Layout

```
helm/
├── Chart.yaml              v0.2.0 — appVersion drives the default image tag for bff/frontend/convertor
├── values.yaml             single source of truth for config + secrets + per-service tunables
├── charts/                 vendored sub-chart .tgz (postgres, minio, rabbitmq, vault, grafana, prometheus, loki, promtail)
└── templates/
    ├── _helpers.tpl        canonical labels, image-ref builder, pod / container security contexts
    ├── configmap.yaml      shared non-secret config (tpl-rendered against .Release.Name)
    ├── secret.yaml         shared Secret; aborts install if JWT_SECRET is missing or <32 chars
    ├── serviceaccount.yaml one SA shared by all pods
    ├── ingress.yaml        single host, path-routed: /api,/docs → backend, / → frontend
    ├── hpa.yaml            consolidated HPAs for the 3 services (per-service toggle)
    ├── pdb.yaml            consolidated PodDisruptionBudgets (per-service toggle)
    ├── migrations-job.yaml pre-install/pre-upgrade hook running `alembic upgrade head`
    ├── backend/            Deployment + Service
    ├── frontend/           Deployment + Service
    ├── convertor/          Deployment + Service (with GPU resource + nodeSelector + tolerations + emptyDir)
    └── tests/test-connection.yaml
```

## Install

```bash
helm dependency update
helm install dev . --namespace video --create-namespace \
  --set 'secret.data.JWT_SECRET=long-random-32-or-more-char-secret'
```

The chart aborts on install if `JWT_SECRET` is empty or under 32 chars — mirrors the BFF's Pydantic fail-fast.

## Upgrade

```bash
helm upgrade dev . --namespace video --reuse-values
```

The migration Job runs as a `pre-upgrade` hook (weight `-5`) before any Deployment is rolled.

## Configuration

Edit `values.yaml` or pass overrides via `-f values.prod.yaml` / `--set`. Highlights:

| Key | Default | Purpose |
| --- | --- | --- |
| `image.registry` | `ghcr.io/feed7362` | Where bff/frontend/convertor images live |
| `image.tag` | `""` (falls back to `Chart.AppVersion`) | Override to ship a specific build |
| `secret.existingSecret` | `""` | Set to point at an externally-managed Secret (ExternalSecrets, Sealed Secrets, …); when empty the chart templates an Opaque Secret from `secret.data` |
| `<svc>.resources` | configured | CPU/mem limits + requests per service |
| `<svc>.probes` | configured | liveness/readiness HTTP paths and timing |
| `<svc>.autoscaling.enabled` | `false` | Toggle HPA per service |
| `<svc>.podDisruptionBudget.enabled` | `false` | Toggle PDB per service |
| `convertor.resources.limits."nvidia.com/gpu"` | `1` | Remove this key to run CPU-only |
| `convertor.nodeSelector` | `nvidia.com/gpu.present: "true"` | Schedule onto labeled GPU nodes; override / null out if your cluster doesn't label nodes that way |
| `migrations.enabled` | `true` | Toggle the Alembic pre-install/upgrade Job |
| `ingress.enabled` | `false` | Turn on the path-routed Ingress (defaults to `nginx` IngressClass on host `video.local`) |
| `serviceAccount.create` / `.name` | `true` / `""` | Use a custom SA (e.g. EKS IRSA) by setting `create: false` + `name: my-sa` |
| `global.imagePullSecrets` | `[]` | Add for private GHCR/Docker Hub |

### Production secrets

Don't ship plaintext `secret.data` to a prod cluster. Two recommended patterns:

**A. External Secrets Operator** (any backend):
```yaml
# Pre-create:
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: video-app, namespace: video }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: aws-sm, kind: SecretStore }
  target: { name: video-app-secret }
  dataFrom:
    - extract: { key: video-streaming/app }
```
Then install:
```bash
helm install dev . -n video --set 'secret.existingSecret=video-app-secret'
```

**B. Sealed Secrets** — `kubeseal` your Secret, commit the ciphertext, point `secret.existingSecret` at its decrypted name.

### GPU scheduling

The convertor requests `nvidia.com/gpu: 1`. For that to satisfy:
- Cluster has the NVIDIA Device Plugin DaemonSet.
- GPU nodes are labeled (`kubectl label node <node> nvidia.com/gpu.present=true`) or you override `convertor.nodeSelector` to match your own labels.
- Or remove the `nvidia.com/gpu` resource entirely + the nodeSelector to fall back to CPU encoding (slow).

### Ingress

Default rules at `video.local`:
- `/api` Prefix → `backend` Service.
- `/docs` Prefix → `backend` Service.
- `/` Prefix → `frontend` Service.

For TLS, fill `ingress.tls`:
```yaml
ingress:
  hosts: [{ host: video.example.com, paths: [...] }]
  tls:
    - secretName: video-tls
      hosts: [ video.example.com ]
```

cert-manager + a `ClusterIssuer` will populate the secret automatically if annotated.

## Verifying before install

```bash
helm lint .
helm template dev . --namespace video --debug | less
helm template dev . --namespace video --set 'secret.data.JWT_SECRET=' --debug
# ↑ should abort with: "secret.data.JWT_SECRET is empty…"
```

## Differences vs the docker-compose stack

| | Compose | Helm |
| --- | --- | --- |
| Vault unseal | sidecar `curlimages/curl` posts to `/v1/sys/unseal` | Bitnami Vault chart; set `vault.server.dev.enabled: true` for dev, or wire Vault Operator for prod |
| nginx gateway | dedicated container with hand-crafted `nginx.conf` | path-routed Ingress (cluster ingress controller does this job) |
| Auto-unseal keys | gitignored `vault/unseal-keys.env` | not present — different unseal strategy in K8s |
| Alertmanager | enabled | enabled (matches compose) |
| Resource limits | `deploy.resources` in compose | full K8s `resources` block with requests + limits |
| Healthchecks | docker `healthcheck:` blocks | K8s `livenessProbe` + `readinessProbe` |
| Migrations | run by bff entrypoint at startup | pre-install/upgrade Job (idempotent, runs once per upgrade) |

## What this chart does **not** include (intentional)

- **NetworkPolicy** — needs per-cluster CNI knowledge; easy to lock yourself out.
- **ExternalSecret CR** — depends on which backend (AWS SM, Vault, GCP SM); generate yourself.
- **KEDA `ScaledObject` for RabbitMQ queue depth** — proper convertor autoscaling signal. Install KEDA separately and add a CR.
- **Service Monitor / PodMonitor CRs** — if you run the kube-prometheus-stack, add these to scrape the bff/ffmpeg services. The bundled Bitnami Prometheus uses static scrape configs instead.

Open an issue or contribute a `templates/networkpolicy.yaml` if you have a known target cluster.
