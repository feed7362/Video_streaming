# StreamHub — Вебплатформа соціальної взаємодії та аналітики мультимедійного контенту

Повнофункціональна мікросервісна платформа відеостримінгу з підтримкою адаптивного HLS-стримінгу, аналітики авторів, повнотекстового пошуку, OAuth-автентифікації та моніторингу в реальному часі.

---

## Технологічний стек

| Рівень | Технологія | Версія |
|--------|-----------|--------|
| **Backend (BFF)** | FastAPI | 0.129 |
| **Frontend** | React + TypeScript + Vite | 19 / 5.8 / 7.x |
| **База даних** | PostgreSQL | 16 |
| **ORM / Міграції** | SQLAlchemy + Alembic | 2.0 |
| **Кеш / Rate limiting** | Redis | latest |
| **Черга повідомлень** | RabbitMQ + FastStream | 3.8 |
| **Об'єктне сховище** | MinIO | latest |
| **Пошуковий рушій** | Elasticsearch | 9.2.0 |
| **Транскодування** | FFmpeg (GPU + CPU fallback) | — |
| **Управління секретами** | HashiCorp Vault | latest |
| **Шлюз** | NGINX | alpine |
| **Моніторинг** | Prometheus + Grafana + Loki | — |
| **Контейнеризація** | Docker + Docker Compose | 24+ |
| **Пакетний менеджер Python** | uv | — |
| **CI/CD** | GitHub Actions | — |

---

## Системні вимоги

| Компонент | Мінімальна версія |
|-----------|------------------|
| Docker Engine | 24.0+ |
| Docker Compose | v2.20+ |
| Python | 3.12+ |
| Node.js | 20+ |
| npm | 10+ |
| uv | 0.4+ |
| Git | 2.40+ |
| RAM | 8 GB |
| Дисковий простір | 20 GB |
| OS | Linux / macOS / Windows 10+ (WSL2) |

---

## Розгортання

### 1. Клонування репозиторію

```bash
git clone https://github.com/feed7362/Video_streaming.git
cd Video_streaming
```

### 2. Налаштування змінних середовища

```bash
cp Docker/.env.example Docker/.env
# Відредагуйте Docker/.env: вкажіть паролі БД, ключі MinIO тощо
```

### 3. Запуск контейнерів

```bash
cd Docker
docker compose up -d
```

Запустяться 15 сервісів: nginx, bff, frontend, convertor, postgres, redis, rabbitmq, minio, elasticsearch, keycloak, vault, prometheus, grafana, loki, promtail.

### 4. Застосування міграцій бази даних

```bash
docker exec bff_service alembic upgrade head
```

### 5. Встановлення залежностей та збірка frontend (для розробки)

```bash
# Backend
cd backend
uv sync

# Frontend
cd frontend
npm install
npm run build
```

### 6. Наповнення тестовими даними (опціонально)

```bash
docker exec bff_service python -m utils.db_seeder
```

### 7. Перевірка стану сервісів

```bash
docker ps
curl http://localhost/api/health/ready
```

---

## Доступ до сервісів

| Сервіс | URL |
|--------|-----|
| Головна сторінка | http://localhost |
| API документація | http://localhost/api/docs |
| Grafana | http://localhost/grafana (admin / admin) |
| MinIO Console | http://localhost/minio/ui |
| RabbitMQ | http://localhost/rabbitmq |

---

## Структура проєкту

```
Video_streaming/
├── Docker/                  # docker-compose.yml, .env, postgres init
├── backend/                 # FastAPI BFF (Python 3.12, uv)
│   ├── src/api/             # REST endpoint handlers (15 роутерів)
│   ├── src/services/        # Бізнес-логіка
│   ├── src/models/          # SQLAlchemy ORM моделі
│   ├── src/infrastructure/  # Клієнти: DB, Redis, MinIO, ES, Vault, RabbitMQ
│   └── alembic/             # Міграції БД
├── frontend/                # React 19 + TypeScript SPA (Vite)
│   └── src/
│       ├── pages/           # 27 сторінок (lazy-loaded)
│       ├── components/      # Спільні UI компоненти
│       └── lib/api/         # Axios API клієнти
├── services/
│   └── convertor/           # FFmpeg мікросервіс транскодування
├── gateway/
│   └── nginx.conf           # Reverse proxy + маршрутизація
├── monitoring/              # Prometheus, Loki, Promtail конфіги
├── vault/                   # HashiCorp Vault auto-unseal
└── ci/                      # GitHub Actions CI/CD workflows
```

---

## Ліцензія

[Apache License 2.0](LICENSE)
