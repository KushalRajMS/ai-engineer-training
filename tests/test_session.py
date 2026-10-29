import pytest
from ai_training.chat.session import ChatSession
from ai_training.providers.mock import MockProvider

def test_add_user_message():
    session = ChatSession(max_history=5)
    session.add_user_message("hello")
    assert len(session.messages) == 2
    assert session.messages[1].role == "user"


def test_empty_user_message_raises():
    session = ChatSession()
    with pytest.raises(ValueError):
        session.add_user_message("   ")


def test_history_is_trimmed():
    session = ChatSession(max_history=2)
    session.add_user_message("one")
    session.add_user_message("two")
    session.add_user_message("three")
    session.trim_history()
    assert len(session.messages) == 3
    assert session.messages[-1].content == "three"


def test_mock_provider_hello_chat():
    session = ChatSession(max_history=5)
    session.add_user_message("hello")
    response = MockProvider().generate(session.get_messages())
    assert "Mock response for: 'hello'" in response

def test_chat_session_with_system_message():
    session = ChatSession()
    assert session.messages[0].role == "system"

def test_windowed_message():
    session = ChatSession(max_pairs=3)
    session.add_user_message("hello")
    session.add_assistant_message("Hello!")
    session.add_user_message("How are you?")
    session.add_assistant_message("Good, you?")
    session.add_user_message("Fine. What a day?")
    session.add_assistant_message("Good sunny day. How are you feeling?")
    session.add_user_message("I am feeling good. What about you?")
    session.add_assistant_message("I am doing. Thanks!")
    expected_len = 7
    actual_len = len(session.get_windowed_messages())
    assert expected_len == actual_len

    expected_tokens = 0
    for message in session.messages:
        content = message.content.split()
        expected_tokens += int(len(content) * 1.3)

    estimated = session.estimate_total_tokens()
    assert expected_tokens == estimated

    session1 = ChatSession()
    session1.add_user_message("hello")
    session1.add_assistant_message("Hello!")
    session1.add_user_message("How are you?")
    session1.add_assistant_message("Good, you?")
    session1.add_user_message("Fine. What a day?")
    session1.add_assistant_message("Good sunny day. How are you feeling?")
    session1.add_user_message("I am feeling good. What about you?")
    session1.add_assistant_message("I am doing. Thanks!")
    expected_len1 = 9
    actual_len1 = len(session1.get_windowed_messages())
    assert expected_len1 == actual_len1

    session2 = ChatSession()
    session2.add_user_message("hello")
    session2.add_assistant_message("Hello!")
    session2.add_user_message("How are you?")
    session2.add_assistant_message("Good, you?")
    session2.add_user_message("Fine. What a day?")
    session2.add_assistant_message("Good sunny day. How are you feeling?")
    session2.add_user_message("I am feeling good. What about you?")
    session2.add_assistant_message("I am doing. Thanks!")
    session2.add_user_message("What is the temparature now in Canada?")
    expected_len2 = 10
    actual_len2 = len(session2.get_windowed_messages())
    assert expected_len2 == actual_len2

    session2.update_system_prompt(profile_name= "code_reviewer")
    metadata = session2.get_metadata_summary()
    assert metadata["mode"] == "code_reviewer"
    session2.clear()
    metadata = session2.get_metadata_summary()
    assert metadata["mode"] == "code_reviewer"