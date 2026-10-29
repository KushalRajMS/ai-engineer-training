import ai_training.chat.chatbot as test_chatbot
from ai_training.chat.chatbot import ChatBot
from ai_training.providers.mock import MockProvider
from ai_training.providers.base import BaseProvider
from ai_training.providers.groq import GroqProvider
import pytest
import json
import httpx

class TestChatBot(BaseProvider):
    def generate(self, message):
        return (f"Simple Test Provider")
    def generate_stream(self, messages):
        yield "Simple Test Provider"

def test_chat_once_with_normal_prompt():
    response, chat_history = test_chatbot.chat_once("hello")
    expected_result = "Mock response for: 'hello'\nModel: mock-model\nStatus: success"
    assert response == expected_result

def test_chat_once_rejects_empty_prompt():
    with pytest.raises(ValueError):
        test_chatbot.chat_once(" ")

def test_chat_once_uses_custom_provider():
    test_provider=TestChatBot()
    response, chat_history = test_chatbot.chat_once("Good Work", provider= test_provider)
    expected_result="Simple Test Provider"
    assert response == expected_result

def test_chat_once_uses_groq_provider():
    groq_provider = GroqProvider()
    chat_history_len1 = 0
    chat_history_len2 = 0
    response, chat_history = test_chatbot.chat_once("Who is Indian Cricket Team Men captain?", provider=groq_provider)
    chat_history_len1 = len(chat_history.get_messages())
    response, chat_history = test_chatbot.chat_once("Can you please share me his stats please.", provider=groq_provider, chat_session=chat_history)
    chat_history_len2 = len(chat_history.get_messages())

    assert chat_history_len2 > chat_history_len1

def test_groq_provider_raises_on_read_timeout(monkeypatch):
    provider = GroqProvider()

    def fake_post(*args, **kwargs):
        raise httpx.ReadTimeout("Timed out while waiting for groq response")

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(ValueError, match="timed out"):
        provider.generate([{"role": "user", "content": "Hello"}])

def test_groq_provide_raises_on_invalid_json(monkeypatch):
    provider = GroqProvider()

    class FakeResponse():
        status_code= 200
        text= "invalid json"

        def json(self):
            raise json.JSONDecodeError("Expecting value", "not valid json", 0)

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(ValueError, match="Unexpected response shape from Groq"):
        provider.generate([{"role": "user", "content": "Hello"}])

def test_groq_provider_raises_when_response_field_is_missing(monkeypatch):
    provider = GroqProvider()

    class FakeResponse:
        status_code= 200
        text= "{}"

        def json(self):
            return {"model": "mistral", "done": True}

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(ValueError, match="Unexpected response shape from Groq"):
        provider.generate([{"role": "user", "content": "Hello"}])

def test_chat_bot_class():
    chat = ChatBot(provider = MockProvider())
    response = chat.send_message("Hello")
    first_message = len(chat.get_history())
    response = chat.send_message("How are you?")
    second_message = len(chat.get_history())
    assert second_message > first_message
    chat.switch_provider(provider= GroqProvider())
    assert isinstance(chat.provider, GroqProvider)
    chat1 = ChatBot(provider= MockProvider(), profile= "code_reviewer")
    response = chat1.send_message("hello")
    chat1_sess = chat1.get_history()
    assert second_message > len(chat1_sess)
    assert len(chat1_sess) == 3
    assert chat1_sess[0]["content"] == "You are a code reviewer. Find bugs, risks, and missing validation."

def test_function_and_class_produce_same_result():
    chat = ChatBot(provider= MockProvider())
    response = chat.send_message("Hello!")
    response1, chat_session = test_chatbot.chat_once(prompt="Hello!", provider= MockProvider())
    assert response == response1
    response = chat.send_message("How are you?")
    response1, chat_session = test_chatbot.chat_once(prompt="How are you?", provider= MockProvider(), chat_session= chat_session)
    assert response == response1

    assert len(chat.get_history()) == len(chat_session.get_messages())

def test_mock_provider_stream():
    chat = ChatBot(provider= MockProvider())
    with pytest.raises(ValueError):
        for _ in chat.stream_message(prompt=" "):
            pass
    response = []
    for reply in chat.stream_message(prompt="Hello, How are you?"):
        response.append(reply)

    assert len(response) > 1
    message= ""
    for i in response:
        message += i

    assert message.strip() != ""

    assert len(chat.get_history()) == 3