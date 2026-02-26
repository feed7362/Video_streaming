import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from prometheus_client import Info

from src.infrastructure.database import engine
from src.infrastructure.elasticsearch import es_client
from src.infrastructure.messaging.client import get_rabbit_broker
from src.infrastructure.redis.client import get_redis
from src.infrastructure.s3_client import get_s3_client
from src.schemas.search import VideoIndexMapping
from src.services.metrics import APP_NAME
from utils.db_seeder import seed_initial_data
from utils.es_reindexer import reindex_videos_from_db

APP_INFO = Info("fastapi_app", "FastAPI Application Information")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    # Prometheus metrics
    APP_INFO.info({"app_name": APP_NAME})

    # Start RabbitMQ
    rabbit_broker = await get_rabbit_broker()
    await rabbit_broker.start()
    logging.info("Rabbit broker connected successfully.")

    # Check S3
    s3_client = get_s3_client()
    await s3_client.check_bucket_exists()
    logging.info("S3 connected successfully and bucket exists.")

    # Seed DB data
    await seed_initial_data()
    logging.info("Created initial data in database.")

    # Ensure the Elasticsearch index exists
    exists = await es_client.indices.exists(index=VideoIndexMapping.index_name)
    if not exists:
        await es_client.indices.create(
            index=VideoIndexMapping.index_name,
            mappings=VideoIndexMapping.mappings,
            settings=VideoIndexMapping.settings,
        )
    logging.info("ElasticSearch index verified/created.")
    logging.info("Startup complete. Metrics exposed.")

    redis = get_redis()
    await redis.ping()
    print("Redis connected successfully.")

    # ─────────────── BACKGROUND TASKS ───────────────
    reindex_task = asyncio.create_task(reindex_videos_from_db(interval_minutes=15))

    logging.info("🚀 Startup complete. Background tasks running.")
    yield

    # Graceful shutdown
    await es_client.close()
    await rabbit_broker.stop()
    logging.info("Rabbit broker connection disposed gracefully.")
    await engine.dispose()
    logging.info("Database engine disposed gracefully.")
    reindex_task.cancel()
    try:
        await reindex_task
    except asyncio.CancelledError:
        logging.info("Reindex task cancelled cleanly.")
    await es_client.close()

    await redis.aclose()
    print("Redis connection closed.")
    logging.info("Background tasks cancelled.")
    logging.info("Shutdown complete.")
