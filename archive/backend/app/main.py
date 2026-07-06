from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.api.entities import router as entities_router

app = FastAPI(
    title="Midwest24 Archive API",
    version="0.1.0",
    description="Institutional memory infrastructure for Midwest24 Archive.",
)

app.include_router(entities_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "midwest24-archive-api"}


@app.get("/health/db", tags=["Health"])
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}
