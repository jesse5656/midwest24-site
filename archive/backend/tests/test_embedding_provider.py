from app.ai.mock_embedding_provider import MockEmbeddingProvider


def test_mock_embedding_provider_returns_vector():
    provider = MockEmbeddingProvider()

    vector = provider.embed("Midwest24 Archive")

    assert isinstance(vector, list)
    assert len(vector) == 16
    assert all(isinstance(value, float) for value in vector)


def test_mock_embedding_provider_is_deterministic():
    provider = MockEmbeddingProvider()

    first = provider.embed("same text")
    second = provider.embed("same text")

    assert first == second
