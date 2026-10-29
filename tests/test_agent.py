from ai_training.langchain_basics.agent import build_agent_prompt, run_agent
from langchain_core.runnables import Runnable
import pytest

def test_build_agent_prompt():
    from ai_training.langchain_basics.agent import build_agent_prompt
    prompt = build_agent_prompt()
    assert prompt is not None

def test_run_agent(monkeypatch):
    from ai_training.langchain_basics.agent import build_agent
    
    class FakeExecutor:
        def invoke(self, inputs):
            return {"output": "The word count is 3."}
    
    monkeypatch.setattr(
        "ai_training.langchain_basics.agent.AgentExecutor",
        lambda **kwargs: FakeExecutor()
    )
    monkeypatch.setattr(
        "ai_training.langchain_basics.agent.create_tool_calling_agent",
        lambda llm, tools, prompt: None
    )
    
    executor = build_agent(None, [])
    result = run_agent(executor, "How many words?")
    assert result == "The word count is 3."