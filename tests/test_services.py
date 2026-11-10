import pytest
from ai_training.api.services import build_store

def test_build_store_empty_raises(monkeypatch):
    monkeypatch.setattr("ai_training.api.services.ingest_documents", lambda path: [])
    with pytest.raises(ValueError):
        build_store("any/dir", "any/store", None)

def test_build_store_returns_chunk_count(monkeypatch):
    saved = {}
    monkeypatch.setattr("ai_training.api.services.ingest_documents", lambda path: ["c1", "c2", "c3"])
    monkeypatch.setattr("ai_training.api.services.create_vector_store", lambda chunks, embedder: "vs")
    monkeypatch.setattr(
        "ai_training.api.services.save_vector_store",
        lambda vs, path: saved.update({"vs": vs, "path": path}),
    )
    assert build_store("any/dir", "out/store", None) == 3
    assert saved == {"vs": "vs", "path": "out/store"}