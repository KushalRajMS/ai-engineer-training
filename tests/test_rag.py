from langchain.schema import Document
from langchain_core.runnables import Runnable
from ai_training.langchain_basics.rag import build_rag_prompt, format_context, run_rag, extract_sources, run_rag_with_sources

def test_format_context():
    docs = [
        Document(page_content="AI is intelligence.", metadata={}),
        Document(page_content="Python is a language.", metadata={})
    ]
    result = format_context(docs)
    assert "AI is intelligence." in result
    assert "Python is a language." in result

def test_build_rag_prompt():
    prompt = build_rag_prompt()
    formatted = prompt.format(context="some context", question="What is AI?")
    assert "some context" in formatted
    assert "What is AI?" in formatted
    assert "I don't know" in formatted

def test_run_rag():
    class FakeRetriever:
        def invoke(self, q):
            return [Document(page_content="Python is a language.", metadata={})]
    
    class FakeLLM:
        def invoke(self, prompt):
            class FakeMsg:
                content = "Python is a programming language."
            return FakeMsg()
    
    result = run_rag(FakeRetriever(), "What is Python?", FakeLLM())
    assert "Python" in result

def test_extract_sources():
    docs = [
        Document(page_content="AI text.", metadata={"source": "file.txt", "chunk_index": 0}),
        Document(page_content="Python text.", metadata={"source": "file2.txt", "chunk_index": 1})
    ]
    sources = extract_sources(docs)
    assert len(sources) == 2
    assert sources[0]["source"] == "file.txt"
    assert sources[1]["chunk_index"] == 1

def test_run_rag_with_sources():
    class FakeRetriever:
        def invoke(self, q):
            return [Document(page_content="Python is a language.", 
                           metadata={"source": "test.txt", "chunk_index": 0})]
    class FakeLLM:
        def invoke(self, prompt):
            class FakeMsg:
                content = "Python is a programming language."
            return FakeMsg()
    
    result = run_rag_with_sources(FakeRetriever(), "What is Python?", FakeLLM())
    assert "answer" in result
    assert "sources" in result
    assert result["sources"][0]["source"] == "test.txt"

def test_build_rag_chain():
    class FakeRetriever:
        def invoke(self, q):
            return [Document(page_content="AI is intelligence.", metadata={})]
        def __or__(self, other):
            from langchain_core.runnables import RunnableLambda
            return RunnableLambda(lambda x: [Document(page_content="AI is intelligence.", metadata={})])

    class FakeLLM(Runnable):
        def invoke(self, prompt, config=None, **kwargs):
            class FakeMsg:
                content = "AI is intelligence."
            return FakeMsg()

    from ai_training.langchain_basics.rag import build_rag_chain
    chain = build_rag_chain(FakeRetriever(), FakeLLM())
    result = chain.invoke("What is AI?")
    assert result.content == "AI is intelligence."