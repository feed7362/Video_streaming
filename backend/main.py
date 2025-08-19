from contextlib import asynccontextmanager
from src.services.rabbit_client import rabbit_broker
from src.api.files import router_files
from src.api.health import router_health
from src.api.metrics import router_metrics, PrometheusMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.i18n import LanguageMiddleware
import logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbit_broker.connect()
    logging.info("Startup complete. Metrics exposed.")
    yield
    logging.info("Shutdown complete.")
    await rabbit_broker.close()


app = FastAPI(title="My API",
              description="BFF",
              version="1.0.0",
              lifespan=lifespan)

# app.mount("/api/metrics", metrics_app)
app.include_router(router_health)
app.include_router(router_files)
app.include_router(router_metrics)
app.add_middleware(LanguageMiddleware)
app.add_middleware(PrometheusMiddleware)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
