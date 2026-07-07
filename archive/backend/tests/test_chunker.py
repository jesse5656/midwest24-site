from app.processing.chunker import Chunker


def test_chunker_returns_single_chunk():
    text = "Hello World"

    chunks = Chunker().chunk(text)

    assert len(chunks) == 1
    assert chunks[0] == "Hello World"


def test_chunker_splits_large_text():
    text = ("Paragraph\n\n" * 300)

    chunks = Chunker().chunk(text, max_chars=250)

    assert len(chunks) > 1
