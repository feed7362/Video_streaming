# Backend Service (BFF)

This directory contains the source code for the Backend-For-Frontend (BFF) service. It is built with FastAPI and serves
as the primary API layer for the application.

## Responsibilities

- Exposing RESTful APIs for file uploads, streaming, and data management.
- Handling business logic and interacting with the PostgreSQL database.
- Interfacing with MinIO for object storage operations.
- Publishing messages to RabbitMQ for asynchronous tasks (e.g., video encoding).
- Exposing application metrics for Prometheus scraping.

## Tech Stack

- **Framework**: FastAPI
- **ORM**: SQLAlchemy with `asyncpg`
- **Migrations**: Alembic
- **Data Validation**: Pydantic
- **Package Management**: `uv`
- **Web Server**: Uvicorn with `uvloop` and `httptools` for high performance.

## API Endpoints

The API is structured with the following primary routers:

- `/api/files`: Endpoints for uploading, streaming, and downloading video files.
- `/api/health`: Liveness probes for health checks.
- `/api/metrics`: Prometheus metrics endpoint.

Detailed API documentation is available via Swagger UI at `/api/docs` when the service is running.

## Environment Variables

The service requires two environment files for configuration:

- `src/database.env`: For PostgreSQL connection details.
- `src/s3.env`: For MinIO (S3) connection details.

Example files (`.env.example`) are provided in the `src/` directory.

## Database Migrations

Database schema migrations are managed with Alembic. Migrations are located in the `alembic/` directory.
