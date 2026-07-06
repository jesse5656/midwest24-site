from fastapi import FastAPI

app = FastAPI(
    title="Midwest24 Archive API",
    version="0.1.0",
    description="Institutional memory infrastructure for Midwest24 Archive.",
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "midwest24-archive-api"}
