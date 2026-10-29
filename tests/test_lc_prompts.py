import pytest
from ai_training.langchain_basics.prompts import summary_template, extraction_template, qa_template

def test_summary_template():
    template= summary_template(style="bullets")
    prompt= template.format(content="Python and RAG and LLM")

    assert "Python and RAG and LLM" in prompt
    assert "{content}" not in prompt

def test_qa_template():
    template= qa_template()
    prompt= template.format(context= "We are discussing about Python Language", question= "Who invented python language?")

    assert "Who invented python language?" in prompt
    assert "{context}" not in prompt

def test_extraction_template():
    template = extraction_template()
    prompt= template.format(fields= "Date, Name, Amount", text= "David got 120 dollars on 18th July 2024.")

    assert "Date, Name, Amount" in prompt
    assert "{text}" not in prompt