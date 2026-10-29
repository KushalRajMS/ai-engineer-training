import pytest
from ai_training.chat.few_shot import FewShot

instruction = "Extract the name, date, and amount from the text below into JSON."

examples = [("Johan paid $50 on March 3rd.", "{\"name\": \"John\", \"date\": \"March 3rd\", \"amount\": 50}"),
            ("Sarah received 120 dollars on July 10.", "{\"name\": \"Sarah\", \"date\": \"July 10\", \"amount\": 120}")]

user_input = "Mike sent 75 dollars on January 5th."

def test_few_shot_with_instruction_and_example():
    prompt = FewShot()
    response = prompt.build_few_shot_prompt(instruction= instruction, examples= examples, user_input= user_input)

    assert response.startswith(instruction)
    assert "Example 1:" in response
    assert response.index("Example 1:") < response.index("Example 2:")
    assert examples[1][0] in response

def test_few_shot_with_instrustion():
    prompt = FewShot()
    response = prompt.build_few_shot_prompt(instruction= instruction, user_input= user_input)
    assert response.endswith(f"Input: {user_input}\nOutput: ")
    assert "Example" not in response

def test_few_shot_with_examples():
    prompt = FewShot()
    response = prompt.build_few_shot_prompt(examples= examples, user_input= user_input)

    assert "Example 2:" in response
    assert instruction not in response
    assert response.index("Example 1:") < response.index("Example 2:")


def test_few_shot_with_fallback():
    prompt = FewShot()

    response = prompt.build_few_shot_prompt(user_input= user_input)
    expected_result = "Mike sent 75 dollars on January 5th."

    assert expected_result == response