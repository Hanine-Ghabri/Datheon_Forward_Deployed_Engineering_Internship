from etl.chunking import semantic_chunks

def test_empty_input():
    assert semantic_chunks("   ") == []

def test_respects_size():
    chunks = semantic_chunks(("Sentence here. " * 100), max_chars=200, overlap=20)
    assert chunks
    assert all(len(c) <= 200 for c in chunks)

def test_preserves_content():
    chunks = semantic_chunks("Alpha sentence. Beta sentence.", max_chars=200, overlap=20)
    assert len(chunks) == 1
    assert "Alpha" in chunks[0] and "Beta" in chunks[0]
