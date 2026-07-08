from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.api.entities import router as entities_router
from app.api.relationships import router as relationships_router
from app.api.tags import router as tags_router
from app.api.entity_tags import router as entity_tags_router
from app.api.search import router as search_router
from app.api.context import router as context_router
from app.api.documents import router as documents_router
from app.api.processing_jobs import router as processing_jobs_router
from app.api.semantic_search import router as semantic_search_router

app = FastAPI(
    title="Midwest24 Archive API",
    version="0.1.0",
    description="Institutional memory infrastructure for Midwest24 Archive.",
)

app.include_router(entities_router)
app.include_router(relationships_router)
app.include_router(tags_router)
app.include_router(entity_tags_router)
app.include_router(search_router)
app.include_router(context_router)
app.include_router(documents_router)
app.include_router(processing_jobs_router)
app.include_router(semantic_search_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "midwest24-archive-api"}


@app.get("/health/db", tags=["Health"])
def database_health_check() -> dict[str, str]:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {"status": "ok", "database": "connected"}
