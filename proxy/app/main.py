from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import account_routes, auth_routes, planner_routes

app = FastAPI(title="Planner Proxy Service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(account_routes.router)
app.include_router(planner_routes.router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
