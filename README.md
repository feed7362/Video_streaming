# Video Streaming Platform

This project is a complete video streaming platform developed using a microservices architecture. It's designed to be
scalable, maintainable, and observable, incorporating modern development practices and a full CI/CD pipeline.

## ✨ Features

- **Microservices Architecture**: Decoupled services for the backend, authentication, video conversion, and moderation.
- **Asynchronous Backend**: Built with **FastAPI** for high performance and handling concurrent operations like file
  uploads and streaming.
- **Modern Frontend**: A responsive user interface built with **React** and **Vite**.
- **Efficient Video Processing**: An asynchronous video conversion service using **FFmpeg** and a message queue (*
  *RabbitMQ**) to handle transcoding tasks.
- **Scalable Storage**: Uses **MinIO** for S3-compatible object storage for video files.
- **Robust CI/CD**: Automated testing, linting, and deployment pipelines using **GitHub Actions**.
- **Comprehensive Observability**: A full monitoring stack with **Prometheus** for metrics, **Loki** for logs, and *
  *Grafana** for visualization and dashboards.
- **Containerized Environment**: The entire application stack is containerized with **Docker** and orchestrated with
  Docker Compose for easy setup and deployment.

## 🏛️ Architecture Overview

The application is composed of several key components that work together:

- **NGINX Gateway**: Acts as a reverse proxy, directing traffic to the appropriate service (frontend or backend).
- **Frontend**: The client-facing React application that users interact with.
- **Backend (BFF)**: A Backend-For-Frontend service built with FastAPI. It handles API requests, manages business logic,
  and communicates with other services and the database.
- **Services**:
    - **Converter Service**: Consumes messages from RabbitMQ to perform video transcoding using FFmpeg.
    - **Auth & Moderation Services**: Dedicated microservices for handling user authentication and content moderation.
- **Data & Messaging**:
    - **PostgreSQL**: The primary relational database for storing application data.
    - **MinIO**: S3-compatible storage for all video assets.
    - **RabbitMQ**: A message broker for queuing asynchronous tasks like video encoding.
- **Observability Stack**:
    - **Prometheus**: Collects metrics from the backend services.
    - **Loki & Promtail**: Aggregate logs from all Docker containers.
    - **Grafana**: Provides dashboards for visualizing logs and metrics.

## 🛠️ Tech Stack

| Category      | Technologies                                                                   |
| :------------ | :----------------------------------------------------------------------------- |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy, Pydantic, Uvicorn, `uv`                      |
| **Frontend** | React, Vite, ESLint, Prettier                                                  |
| **Database** | PostgreSQL, Alembic (Migrations)                                               |
| **Services** | RabbitMQ (Message Broker), FFmpeg (Video Processing)                           |
| **Storage** | MinIO (S3-Compatible Object Storage)                                           |
| **DevOps** | Docker, Docker Compose, GitHub Actions, NGINX, Pre-commit, Gitleaks, Dependabot |
| **Monitoring**| Prometheus, Grafana, Loki, Promtail                                            |

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- An NVIDIA GPU with the NVIDIA Container Toolkit is required for the FFMPEG conversion service.

### Running Locally

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Prepare Environment Files:**
   Copy the example environment files and populate them with your secrets if necessary.
   ```bash
   cp backend/src/database.env.example backend/src/database.env
   cp backend/src/s3.env.example backend/src/s3.env
   ```

3. **Build and Run the Stack:**
   Use the following Docker Compose commands from the root directory.
   ```bash
   # Build all the service images
   docker compose -p video_streaming_stack -f ./Docker/docker-compose.yml build

   # Start all services in detached mode
   docker compose -p video_streaming_stack -f ./Docker/docker-compose.yml up -d
   ```

4. **Accessing Services:**
    - **Frontend Application**: `http://localhost`
    - **Backend API Docs**: `http://localhost/api/docs`
    - **Grafana Dashboard**: `http://localhost/grafana` (user: `admin`, pass: `admin`)
    - **MinIO Console**: `http://localhost/minio/ui`

## CI/CD Pipeline

This project is configured with a complete CI/CD pipeline using GitHub Actions:

1. **Push to `dev` branch**: Triggers the `CI for dev branch` workflow, which runs linting, type-checking, tests, and
   security scans for all services.
2. **Successful CI on `dev`**: Automatically triggers the `Auto PR to Stage` workflow, which creates a pull request from
   `dev` to the `stage` branch.
3. **Merge to `stage` branch**: Triggers the `CD Pipeline` workflow, which detects changed services, builds their Docker
   images, and (optionally) deploys them.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Set up the pre-commit hooks to ensure code quality: `pre-commit install`.
4. Make your changes.
5. Submit a pull request.

Please use the provided templates for submitting [bug reports](.github/ISSUE_TEMPLATE/bug_report.md)
and [feature requests](.github/ISSUE_TEMPLATE/feature_request.md).

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
