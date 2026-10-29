from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda

@tool
def get_word_count(text: str) -> int:
    """Returns the number of words in a given text."""
    return len(text.split())

@tool
def get_char_count(text: str) -> int:
    """Returns the number of characters in a given text."""
    return len(text)

@tool
def summarize_text(text: str) -> str:
    """Returns a brief preview of the text."""
    return text[:100] + "..."

@tool
def divide(num1: float, num2: float) -> str:
    """Divides num1 by num2 safely."""
    try:
        return str(num1 / num2)
    except ZeroDivisionError:
        raise ValueError("Error: Cannot divide by zero.")

def get_tool_registry():
    return [get_word_count, get_char_count, summarize_text, divide]

def normalise_output(tool_name, result, success):
    return {
        "tool_name": tool_name,
        "result": result,
        "success": success,
    }

def create_normalised_tool(tool_fn):
    def wrapper(inputs):
        try:
            result= tool_fn.invoke(inputs)
            return normalise_output(tool_fn.name, result, True)
        except Exception as e:
            return normalise_output(tool_fn.name, str(e), False)
    return RunnableLambda(wrapper)

def get_normalised_registry():
    results= []
    for tool in get_tool_registry():
        results.append(create_normalised_tool(tool))
    return results

if __name__ == "__main__":
    text= "Artificial Intelligence is the field of computer science focused on building systems that can perform tasks that typically require human intelligence. These tasks include understanding language, recognising patterns, making decisions, and solving problems. Modern AI systems are powered by machine learning models that learn from large amounts of data rather than following hand written rules."

    print(get_word_count.invoke({"text": text}))
    print(get_char_count.invoke({"text": text}))
    print(summarize_text.invoke({"text": text}))

    for t in get_tool_registry():
        print(t.name, "—", t.description)

    registry = get_normalised_registry()
    print(registry[0].invoke({"text": "hello world"}))
    print(registry[3].invoke({"num1": 10.0, "num2": 0.0}))