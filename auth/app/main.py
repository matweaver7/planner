from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.database import dispose_engine, get_conn, init_engine
from app.routers import auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_engine()
    yield
    await dispose_engine()


app = FastAPI(title="Planner Auth Service", version="0.1.0", lifespan=lifespan)

app.include_router(auth_router.router)


@app.get("/health")
async def health(conn: AsyncConnection = Depends(get_conn)) -> dict:
    await conn.execute(text("SELECT 1"))
    return {"status": "ok"}
