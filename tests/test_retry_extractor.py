import pytest
from ai_training.chat.retry_extractor import RetryExtractor
from ai_training.providers.base import BaseProvider
from ai_training.providers.groq import GroqProvider

instruction = "Extract the name, date, and amount from the text below into JSON."

examples = [("Johan paid $50 on March 3rd.", "{\"name\": \"John\", \"date\": \"March 3rd\", \"amount\": 50}"),
            ("Sarah received 120 dollars on July 10.", "{\"name\": \"Sarah\", \"date\": \"July 10\", \"amount\": 120}")]

user_input = "Mike sent 75 dollars on January 5th."
required_keys = ["name", "date", "amount"]

class StubProvider(BaseProvider):
    def __init__(self, responses: list[str]) -> str:
        self.response = responses
        self.call_count = 0
    def generate(self, messages: list[dict[str, str]]) -> str:
        response = self.response[self.call_count]
        self.call_count += 1
        return response
    def generate_stream(self, messages):
        yield "Simple Test Provider"


def test_extract_with_retry_with_stud():
    extractor = RetryExtractor()

    stub = StubProvider(responses= [
    '{"name": "Mike", "date": "January 5th", "amount": 75}'
    ])
    result = extractor.extract_with_retry(provider= stub, instruction= instruction, examples= examples, user_input= user_input, required_keys= required_keys, max_retries= 3)

    assert result == {"name": "Mike", "date": "January 5th", "amount": 75}
    assert stub.call_count == 1

    stub = StubProvider(responses= [
        "not valid json",
        "nope",
        '{"name": "Mike", "date": "January 5th", "amount": 75}'
    ])
    result = extractor.extract_with_retry(provider= stub, instruction= instruction, examples= examples, user_input= user_input, required_keys= required_keys, max_retries= 3)
    assert result == {"name": "Mike", "date": "January 5th", "amount": 75}
    assert stub.call_count == 3

    stub = StubProvider([
        "invalid",
        "invalid",
        "invalid",
        "invalid"
    ])
    result = extractor.extract_with_retry(provider= stub, instruction= instruction, examples= examples, user_input= user_input, required_keys= required_keys, max_retries= 4)
    assert result is None
    assert stub.call_count == 4

def test_build_emphasis_instruction():
    extractor = RetryExtractor()
    response = extractor.build_emphasis_instruction(instruction=instruction, required_keys= required_keys, retry= 1)
    assert "valid JSON" in response
    assert "date" in response
    response = extractor.build_emphasis_instruction(instruction=instruction, required_keys= required_keys, retry= 2)
    assert "No explanation" in response
    assert "amount" in response
    response = extractor.build_emphasis_instruction(instruction=instruction, required_keys= required_keys, retry= 3)
    assert "CRITICAL" in response
    response = extractor.build_emphasis_instruction(instruction=instruction, required_keys= required_keys, retry= 4)
    assert "CRITICAL" in response