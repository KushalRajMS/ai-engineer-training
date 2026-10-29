from langchain.schema import Document
from ai_training.langchain_basics.vector_store import create_vector_store, save_vector_store, load_vector_store, search, search_with_scores, make_retriever
import pytest

class FakeVectorStore:
    def similarity_search(self, query, k=3):
        return [Document(page_content="Test content.", metadata={"source": "test"})]
    
    def save_local(self, path):
        pass
    
    def similarity_search_with_score(self, query, k=3):
        return [(Document(page_content="Test content.", metadata={"source": "test"}), 0.5)]
    
    def as_retriever(self, search_kwargs=None):
        return self
    
    def invoke(self, query):
        return [Document(page_content="Test content.", metadata={"source": "test"})]
    
def test_search():
    vs = FakeVectorStore()
    results = search(vs, "AI", k=1)
    assert len(results) == 1
    assert isinstance(results[0], Document)

def test_save_vector_store(tmp_path):
    vs = FakeVectorStore()
    save_vector_store(vs, str(tmp_path / "vs"))

def test_load_vector_store(tmp_path, monkeypatch):
    from ai_training.langchain_basics import vector_store as vs_module
    monkeypatch.setattr(vs_module.FAISS, "load_local", lambda *args, **kwargs: FakeVectorStore())
    loaded = load_vector_store(str(tmp_path / "vs"), None)
    assert loaded is not None

def test_make_retriever():
    vs = FakeVectorStore()
    retriever = make_retriever(vs, k=2)
    assert retriever is not None

def test_search_with_scores():
    vs = FakeVectorStore()
    results = search_with_scores(vs, "AI", k=1)
    assert len(results) == 1
    assert isinstance(results[0][0], Document)
    assert isinstance(results[0][1], float)