from app.ai.mock_embedding_provider import MockEmbeddingProvider
from app.repositories.semantic_search_repository import SemanticSearchRepository


class SemanticSearchService:
    def __init__(self, db):
        self.provider = MockEmbeddingProvider()
        self.repository = SemanticSearchRepository(db)

    def search(self, query: str, limit: int = 10):
        vector = self.provider.embed(query)
        return self.repository.search_chunks(vector, limit)
