# Observability Stack

This directory contains the configuration files for the project's monitoring and observability stack. This stack
provides crucial insights into the application's performance, health, and behavior.

## Components

- **Prometheus (`prometheus.yaml`)**:
    - A time-series database that scrapes and stores metrics from our services. It is configured to scrape the
      `/api/metrics` endpoint of the FastAPI backend and other services.

- **Loki (`loki-config.yaml`)**:
    - A log aggregation system designed to store and query logs efficiently. It collects logs from all running
      containers.

- **Promtail (`promtail-config.yaml`)**:
    - The agent responsible for collecting logs from Docker containers and shipping them to Loki. It is configured to
      parse Docker's JSON log format and enrich logs with useful labels like `container_name`.

- **Grafana (`datasources.yaml`, `dashboard.json`)**:
    - A visualization platform for creating dashboards from various data sources.
    - `datasources.yaml`: Provisions Prometheus and Loki as default data sources.
    - `dashboard.json`: A pre-configured dashboard for monitoring the FastAPI application, displaying key metrics like
      request latency, error rates, and throughput, as well as application logs from Loki.

## Accessing Dashboards

- **Grafana**: `http://localhost/grafana`
    - **Username**: `admin`
    - **Password**: `admin`
- **Prometheus**: `http://localhost:9090`
- **MinIO Console**: `http://localhost/minio/ui`
