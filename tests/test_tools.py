from ai_training.langchain_basics.tools import get_word_count, get_char_count, summarize_text, get_tool_registry, divide
import pytest

def test_get_word_count():
    result = get_word_count.invoke({"text": "hello world foo"})
    assert result == 3

def test_get_char_count():
    result = get_char_count.invoke({"text": "hello"})
    assert result == 5

def test_summarize_text():
    result = summarize_text.invoke({"text": "word " * 50})
    assert result.endswith("...")
    assert len(result) <= 103

def test_get_tool_registry():
    tools = get_tool_registry()
    assert len(tools) == 4
    names = [t.name for t in tools]
    assert "get_word_count" in names

def test_safe_divide_normal():
    result = divide.invoke({"num1": 10.0, "num2": 2.0})
    assert result == "5.0"

def test_safe_divide_by_zero():
    from ai_training.langchain_basics.tools import divide
    
    # Update the test case to expect the ValueError
    with pytest.raises(ValueError) as exc_info:
        divide.invoke({"num1": 10.0, "num2": 0.0})
        
    assert str(exc_info.value) == "Error: Cannot divide by zero."

def test_normalise_output():
    from ai_training.langchain_basics.tools import normalise_output
    result = normalise_output("get_word_count", 5, True)
    assert result["tool_name"] == "get_word_count"
    assert result["result"] == 5
    assert result["success"] == True

def test_create_normalised_tool():
    from ai_training.langchain_basics.tools import create_normalised_tool, get_word_count
    normalised = create_normalised_tool(get_word_count)
    result = normalised.invoke({"text": "hello world"})
    assert result["success"] == True
    assert result["result"] == 2

def test_normalised_tool_failure():
    from ai_training.langchain_basics.tools import create_normalised_tool, divide
    normalised = create_normalised_tool(divide)
    result = normalised.invoke({"num1": 10.0, "num2": 0.0})
    assert result["success"] == False
    assert "Error" in result["result"]