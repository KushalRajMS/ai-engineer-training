import pytest
from ai_training.chat.profiles import get_prompt

def test_get_prompt_with_code_reviewer():
    retrived_prompt = get_prompt("code_reviewer")
    expected_prompt = "You are a code reviewer. Find bugs, risks, and missing validation."
    assert expected_prompt == retrived_prompt

def test_get_prompt_with_wrong_role():
    retrived_prompt = get_prompt("ai_reviewer")
    expected_prompt = "You are a useful assistant"
    assert expected_prompt == retrived_prompt