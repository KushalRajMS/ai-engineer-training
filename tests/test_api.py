from fastapi.testclient import TestClient
from ai_training.api.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

def test_ask_returns_answer(monkeypatch):
    monkeypatch.setattr("ai_training.api.main.load_vector_store", lambda store, embedder: None)
    monkeypatch.setattr("ai_training.api.main.make_retriever", lambda vs, k: None)
    monkeypatch.setattr("ai_training.api.main.make_llm", lambda: None)
    monkeypatch.setattr("ai_training.api.main.get_embedder", lambda: None)
    monkeypatch.setattr(
        "ai_training.api.main.run_rag_with_sources",
        lambda retriever, question, llm: {
            "answer": "AI is intelligence.",
            "sources": [{"source": "file.txt", "chunk_index": 0}],
        },
    )
    response = client.post("/ask", json={"question": "What is AI?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "AI is intelligence."

def test_ask_missing_question_returns_422():
    response = client.post("/ask", json={"k": 2})
    assert response.status_code == 422

def test_ask_blank_question_returns_422():
    response = client.post("/ask", json={"question": "   "})
    assert response.status_code == 422

def test_ask_invalid_k_returns_422():
    response = client.post("/ask", json={"question": "What is AI?", "k": 0})
    assert response.status_code == 422

def test_ask_missing_store_returns_404(monkeypatch, tmp_path):
    monkeypatch.setattr("ai_training.api.main.ARTIFACTS_DIR", tmp_path)
    response = client.post("/ask", json={"question": "What is AI?"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_ask_llm_failure_returns_502(monkeypatch, tmp_path):
    (tmp_path / "vector_store").mkdir()
    monkeypatch.setattr("ai_training.api.main.ARTIFACTS_DIR", tmp_path)
    monkeypatch.setattr("ai_training.api.main.get_embedder", lambda: None)
    monkeypatch.setattr("ai_training.api.main.load_vector_store", lambda store, embedder: None)
    monkeypatch.setattr("ai_training.api.main.make_retriever", lambda vs, k: None)
    monkeypatch.setattr("ai_training.api.main.make_llm", lambda: None)

    def fail(retriever, question, llm):
        raise ValueError("timeout")

    monkeypatch.setattr("ai_training.api.main.run_rag_with_sources", fail)
    response = client.post("/ask", json={"question": "What is AI?"})
    assert response.status_code == 502

def _patch_pipeline(monkeypatch, tmp_path, chunks):
    monkeypatch.setattr("ai_training.api.main.ARTIFACTS_DIR", tmp_path)
    monkeypatch.setattr("ai_training.api.main.get_embedder", lambda: None)

    def fake_build_store(upload_dir, store_path, embedder):
        if not chunks:
            raise ValueError("No content to index.")
        return len(chunks)

    monkeypatch.setattr("ai_training.api.main.build_store", fake_build_store)
    
def test_ingest_success(monkeypatch, tmp_path):
    _patch_pipeline(monkeypatch, tmp_path, ["c1", "c2"])
    response = client.post("/ingest", files={"file": ("notes.txt", b"hello world", "text/plain")})
    assert response.status_code == 200
    assert response.json()["chunks"] == 2
    assert (tmp_path / "uploads" / "notes.txt").exists()

def test_ingest_wrong_extension_returns_415(monkeypatch, tmp_path):
    _patch_pipeline(monkeypatch, tmp_path, ["c1"])
    response = client.post("/ingest", files={"file": ("run.exe", b"x", "application/octet-stream")})
    assert response.status_code == 415

def test_ingest_too_large_returns_413(monkeypatch, tmp_path):
    _patch_pipeline(monkeypatch, tmp_path, ["c1"])
    monkeypatch.setattr("ai_training.api.main.MAX_FILE_SIZE", 5)
    response = client.post("/ingest", files={"file": ("big.txt", b"123456", "text/plain")})
    assert response.status_code == 413

def test_ingest_no_chunks_returns_400(monkeypatch, tmp_path):
    _patch_pipeline(monkeypatch, tmp_path, [])
    response = client.post("/ingest", files={"file": ("empty.txt", b"", "text/plain")})
    assert response.status_code == 400
    assert not (tmp_path / "uploads" / "empty.txt").exists()

def test_ingest_strips_folder_from_filename(monkeypatch, tmp_path):
    _patch_pipeline(monkeypatch, tmp_path, ["c1"])
    client.post("/ingest", files={"file": ("../../evil.txt", b"hi", "text/plain")})
    assert (tmp_path / "uploads" / "evil.txt").exists()
    assert not (tmp_path.parent / "evil.txt").exists()