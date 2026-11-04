import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import dispose_engine, get_conn, init_engine
from app.routers import accounts as accounts_router

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        # Quiet noisy third-party loggers
        "loggers": {
            "uvicorn": {"level": "INFO"},
            "uvicorn.access": {"level": "INFO"},
            "asyncio": {"level": "WARNING"},
        },
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_engine()
    yield
    await dispose_engine()


app = FastAPI(title="Planner Accounts Service", version="0.1.0", lifespan=lifespan)

app.include_router(accounts_router.router)


@app.get("/health")
async def health(conn: AsyncConnection = Depends(get_conn)) -> dict:
    await conn.execute(text("SELECT 1"))
    return {"status": "ok"}
