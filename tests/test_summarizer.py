import pytest
from ai_training.providers.base import BaseProvider
from ai_training.pipeline.summarizer import Summarizer

class StudProvider(BaseProvider):
    def generate(self, messages):
        self.messages = messages[1]["content"][48:]
        if self.messages == "":
            return("")
        return f"File contains {self.messages}"
    def generate_stream(self, messages):
        yield "Simple Test Provider"


def test_build_summary_prompt():
    summary_provider = Summarizer()
    response = summary_provider.build_summary_prompt("Hello!")
    assert response == "Summarize the following text in 2-3 sentences:\n\nHello!"

def test_summarize_file():
    test_provider = StudProvider()
    summary_provider = Summarizer()
    response = summary_provider.summarize_file({"filename": "file1.txt", "content": "Hello World!"}, provider= test_provider)
    assert response["filename"] == "file1.txt"
    assert "summary" in response
    assert response["success"] == True
    response = summary_provider.summarize_file({"filename": "file1.txt", "content": ""}, provider= test_provider)
    assert response["filename"] == "file1.txt"
    assert "summary" in response
    assert response["success"] == False

def test_summarize_batch():
    test_provider = StudProvider()
    summary_provider = Summarizer()
    files: list[dict] =[
        {"filename": "file1.txt", "content": "hello"},
        {"filename": "file2.txt"},
        {"filename": "file2.txt", "content": "Hello World!"},
    ]
    response = summary_provider.summarize_batch(files= files, provider= test_provider)
    assert len(files) == len(response)
    assert response[1]["summary"] == None