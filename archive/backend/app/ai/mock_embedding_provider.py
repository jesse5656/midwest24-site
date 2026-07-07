import hashlib


class MockEmbeddingProvider:
    def embed(self, text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()

        return [
            round(byte / 255, 6)
            for byte in digest[:16]
        ]
