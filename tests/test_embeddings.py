import pytest
from ai_training.langchain_basics.embeddings import embed_chunks, embed_query
from langchain.schema import Document

class FakeEmbedder:
    def embed_query(self, text):
        return [0.1] * 384
    def embed_documents(self, texts):
        return[[0.1] * 384 for _ in texts]

@pytest.fixture
def fake_embedder():
    return FakeEmbedder()

def test_embed_query_returns_vector(fake_embedder):
    vector= embed_query(fake_embedder, "What is AI?")
    assert isinstance(vector, list)
    assert len(vector) == 384

def test_embed_chunks(fake_embedder):
    docs=[
        Document(page_content="AI is transforming the world.", metadata={}),
        Document(page_content="Python is a popular language.", metadata={})
    ]
    vectors= embed_chunks(fake_embedder, docs)
    assert len(vectors) == 2
    assert len(vectors[0]) == 384