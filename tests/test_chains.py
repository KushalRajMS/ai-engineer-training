import pytest
from ai_training.langchain_basics.chains import run_summary_chain, run_qa_chain, run_extraction_chain

def test_run_summary_chain(monkeypatch):
    monkeypatch.setattr("ai_training.langchain_basics.chains.run_summary_chain", lambda content, style: "fake response")
    result = run_summary_chain(content="Python is great.", style="brief")
    assert result != ""

def test_run_qa_chain(monkeypatch):
    monkeypatch.setattr("ai_training.langchain_basics.chains.run_qa_chain", lambda context, question: "fake response")
    result = run_qa_chain(context="Python was created by Guido.", question="Who created Python?")
    assert result != ""

def test_run_extraction_chain(monkeypatch):
    monkeypatch.setattr("ai_training.langchain_basics.chains.run_extraction_chain", lambda text, fields: "fake response")
    result = run_extraction_chain(text="David paid 100 dollars.", fields="Name, Amount")
    assert result != ""