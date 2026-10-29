from langchain.schema import Document
from ai_training.langchain_basics.splitters import split_documents, get_chunk_stats, enrich_chunk_metadata

def test_split_produces_chunks():
    doc= Document(page_content="word " * 100, metadata={"source": "test"})
    chunks= split_documents([doc], chunk_size=50, chunk_overlap=10)
    assert len(chunks) > 1

def test_get_chunk_stats():
    doc= Document(page_content="word " * 100, metadata= {"source": "test"})
    chunks= split_documents([doc], chunk_size=50, chunk_overlap=10)
    stats= get_chunk_stats(chunks= chunks)
    assert stats["total_chunks"] > 1
    assert stats["max_chunk_size"] >= stats["min_chunk_size"]

def test_enrich_chunk_metadata():
    doc= Document(page_content="word " * 100, metadata={"source": "test"})
    chunks= split_documents([doc], chunk_size=50, chunk_overlap=10)
    enriched= enrich_chunk_metadata(chunks=chunks, doc_id="test_doc")
    assert enriched[0].metadata['chunk_index'] == 0
    assert enriched[0].metadata["doc_id"] == "test_doc"
    assert "chunk_size" in enriched[0].metadata