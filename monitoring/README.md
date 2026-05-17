# Observability stack

Prometheus + Alertmanager + Loki + Promtail + Grafana. Wired into both the Docker Compose stack and the Helm chart.

## Components

| File | Component | Notes |
| ---- | --------- | ----- |
| `prometheus.yaml`     | Prometheus | Scrapes bff + ffmpeg `/api/metrics`; loads rules from `alert.rules.yml`; ships alerts to Alertmanager. |
| `alert.rules.yml`     | Prometheus rules | 5 starter alerts (see below). |
| `alertmanager.yml`    | Alertmanager | Routes critical alerts immediately, batches warnings; webhook receiver is a stub — wire to Slack / Discord / email in your real env. |
| `loki-config.yaml`    | Loki | Single-binary log store. |
| `promtail-config.yaml`| Promtail | Tails `/var/lib/docker/containers/**/*.log`; parses Docker JSON; extracts labels (`container_name`, `image_name`). |
| `datasources.yaml`    | Grafana provisioning | Prometheus + Loki preconfigured. |
| `dashboard.json`      | Grafana dashboard | App-level latency / errors / throughput / logs. |

## Alert rules

| Alert | Triggers when | Severity |
| ----- | ------------- | -------- |
| `ServiceDown`           | `up == 0` for 2 min | critical |
| `HighHttp5xxRate`       | 5xx rate > 5 % over 5 min | warning |
| `HttpRequestLatencyHigh`| p95 latency > 2 s for 10 min | warning |
| `ConvertorEncodeFailures` | `up{job="ffmpeg"} == 0` for 1 min | critical |
| `ProcessRestartLoop`    | `>3` `process_start_time_seconds` changes in 10 min | warning |

Add new rules by editing `alert.rules.yml`, then either reload Prometheus (`curl -X POST http://localhost:9090/-/reload`, enabled via `--web.enable-lifecycle`) or restart the container.

## Receivers

`alertmanager.yml` defines one receiver named `default` with a placeholder webhook URL. **Alerts fire silently until you swap that for a real destination.** Examples:

```yaml
# Slack
slack_configs:
  - api_url: "https://hooks.slack.com/services/…"
    channel: "#alerts"

# Discord — use Slack-compatible webhook URL
webhook_configs:
  - url: "https://discord.com/api/webhooks/…/slack"
    send_resolved: true

# Email
email_configs:
  - to: "ops@example.com"
    from: "alerts@example.com"
    smarthost: "smtp.example.com:587"
    auth_username: "alerts@example.com"
    auth_identity: "alerts@example.com"
    auth_password: "$SMTP_PASS"
```

## Accessing dashboards

| Service | URL | Credentials |
| ------- | --- | ----------- |
| Grafana | `http://localhost/grafana` | `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD` from `Docker/.env`. **No longer `admin/admin`** — compose refuses to start with unset values. |
| Prometheus | inside the docker network at `http://prometheus:9090`; exposed via gateway under `/prometheus/` | none |
| Alertmanager | in-cluster only; reach with `docker exec alertmanager wget -qO- http://localhost:9093/api/v2/status` | none |
| MinIO Console | `http://localhost/minio/ui` | `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` from `Docker/.env` |

## Tracing requests across services

Every HTTP request gets an `X-Request-ID` propagated through RabbitMQ into the convertor. Each log line carries `[rid=<uuid>]`. To follow one request:

```bash
curl -H "X-Request-ID: trace-demo" http://localhost/api/videos/?page=1
docker logs bff_service     2>&1 | grep trace-demo
docker logs ffmpeg_service  2>&1 | grep trace-demo
```

In Loki:
```logql
{container_name=~"bff_service|ffmpeg_service"} |= "trace-demo"
```

## Image pins

All monitoring images are pinned to specific versions in `Docker/docker-compose.yml` to avoid silent upgrades:

| Service | Tag |
| ------- | --- |
| prometheus | `v2.55.1` |
| alertmanager | `v0.27.0` |
| grafana | `11.3.1` |
| loki | `3.3.2` |
| promtail | `3.3.2` |

Bump intentionally; never use `:latest` in this project.
