from app.ai.mock_embedding_provider import MockEmbeddingProvider
from app.core.config import settings


def get_embedding_provider():
    if settings.embedding_provider == "mock":
        return MockEmbeddingProvider()

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
