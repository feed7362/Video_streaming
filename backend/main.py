from contextlib import asynccontextmanager

from src.services.rabbit_client import rabbit_broker
from src.api.files import router_files
from src.api.health import router_health
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.i18n import LanguageMiddleware
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbit_broker.connect()
    yield
    await rabbit_broker.close()


app = FastAPI(title="My API",
              description="BFF",
              version="1.0.0",
              lifespan=lifespan)
app.include_router(router_health)
app.include_router(router_files)
app.add_middleware(LanguageMiddleware)

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


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
