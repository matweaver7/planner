from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import connect, disconnect
from app.routers import daily, monthly, weekly


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    yield
    await disconnect()


app = FastAPI(title="Planner Data Service", version="0.1.0", lifespan=lifespan)

app.include_router(daily.router)
app.include_router(weekly.router)
app.include_router(monthly.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
