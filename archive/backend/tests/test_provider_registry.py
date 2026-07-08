from app.ai.mock_embedding_provider import MockEmbeddingProvider
from app.ai.provider_registry import get_embedding_provider


def test_provider_registry_returns_mock_provider():
    provider = get_embedding_provider()

    assert isinstance(provider, MockEmbeddingProvider)
