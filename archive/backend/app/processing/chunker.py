class Chunker:
    def chunk(self, text: str, max_chars: int = 1000):
        text = text.strip()

        if not text:
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        chunks = []
        current = ""

        for paragraph in paragraphs:
            candidate = paragraph if not current else current + "\n\n" + paragraph

            if len(candidate) <= max_chars:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = paragraph

        if current:
            chunks.append(current)

        return chunks
