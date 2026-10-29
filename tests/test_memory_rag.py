from ai_training.langchain_basics.memory_rag import build_contextualize_prompt, build_memory_retriever
from langchain_core.messages import HumanMessage, AIMessage
from langchain.schema import Document
from langchain_core.runnables import Runnable, RunnableLambda

def test_build_contextualize_prompt():
    prompt = build_contextualize_prompt()
    assert prompt is not None

def test_build_memory_retriever(monkeypatch):    
    class FakeRetriever(Runnable):
        def invoke(self, input, config=None, **kwargs):
            return [Document(page_content="Python is a language.", metadata={})]
    
    class FakeLLM(Runnable):
        def invoke(self, prompt, config=None, **kwargs):
            class FakeMsg:
                content = "What is Python?"
            return FakeMsg()
    
    monkeypatch.setattr(
        "ai_training.langchain_basics.memory_rag.create_history_aware_retriever",
        lambda llm, retriever, prompt: RunnableLambda(
            lambda x: [Document(page_content="Python is a language.", metadata={})]
        )
    )
    
    memory_retriever = build_memory_retriever(FakeRetriever(), FakeLLM())
    result = memory_retriever.invoke({"input": "What is Python?", "chat_history": []})
    assert len(result) > 0
    assert isinstance(result[0], Document)

def test_run_conversation_rag(monkeypatch):
    from langchain_core.runnables import RunnableLambda
    from langchain_core.messages import HumanMessage, AIMessage
    from ai_training.langchain_basics.memory_rag import run_conversation_rag

    memory_retriever = RunnableLambda(
        lambda x: [Document(page_content="Python is a language.", metadata={"source": "test.txt", "chunk_index": 0})]
    )

    class FakeLLM(Runnable):
        def invoke(self, prompt, config=None, **kwargs):
            class FakeMsg:
                content = "Python is a programming language."
            return FakeMsg()

    results = run_conversation_rag(memory_retriever, FakeLLM(), ["What is Python?", "What is it used for?"])
    assert len(results) == 2
    assert results[0]["question"] == "What is Python?"
    assert "answer" in results[0]
    assert "sources" in results[0]