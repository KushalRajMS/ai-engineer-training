from pathlib import Path
from ai_training.langchain_basics.ingestion import ingest_documents
from ai_training.langchain_basics.vector_store import save_vector_store, create_vector_store

def build_store(upload_dir, store_path, embedder):
    chunks= ingest_documents(str(upload_dir))
    if not chunks:
        raise ValueError("No content to index.")
    vector_store= create_vector_store(chunks, embedder)
    save_vector_store(vector_store, store_path)
    return len(chunks)

def clean_sources(sources):
    return [
        {"source": Path(s["source"]).name, "chunk_index": s.get("chunk_index")} for s in sources
    ]