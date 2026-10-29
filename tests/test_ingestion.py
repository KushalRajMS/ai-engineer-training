import pytest
from ai_training.langchain_basics.ingestion import ingest_documents

def test_ingest_txt_file(tmp_path):
    f= tmp_path / "test.txt"
    f.write_text("word " * 200)
    chunks= ingest_documents(str(f), chunk_size= 50, chunk_overlap= 10)
    assert len(chunks) > 1
    assert chunks[0].metadata["doc_id"] == 'test.txt'
    assert "chunk_index" in chunks[0].metadata

def test_ingest_directory(tmp_path):
    (tmp_path / "file1.txt").write_text("word " * 200)
    (tmp_path / "file2.txt").write_text("word " * 200)
    chunks= ingest_documents(str(tmp_path), chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1