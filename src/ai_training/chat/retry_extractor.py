from __future__ import annotations
from ai_training.chat.few_shot import FewShot
from ai_training.chat.chatbot import chat_once
from ai_training.chat.output_validator import OutputValidator
from ai_training.providers.groq import GroqProvider

class RetryExtractor:
    def build_emphasis_instruction(self, instruction: str, required_keys: list[str], retry: int) -> str:
        keys_text= ", ".join(required_keys)
        escalation_level = min(retry, 3)

        if escalation_level == 1:
            emphasis = f"Please make sure to return valid JSON with these keys: {keys_text}."
        elif escalation_level == 2:
            emphasis = (
                f"You must return ONLY a JSON object with exactly these keys: {keys_text}. "
                f"No explanation, no extra text."
            )
        else:
            emphasis=(
                f"CRITICAL: Return ONLY a valid JSON object with EXACTLY these keys: {keys_text}. "
                f"Absolutely no explaination, no markdown, no extra words - the response must be "
                f"parseable JSON and nothing else."
            )

        return(
            f"{instruction}\n\n{emphasis}")

    def extract_with_retry(self, provider, instruction: str, examples: list[tuple[str, str]], user_input: str, required_keys: list[str], max_retries: int = 3) -> dict|None:
        prompt_provider = FewShot()
        output_validator = OutputValidator()
        current_instruction = instruction
        retries = 0

        while retries < max_retries:
            prompt = prompt_provider.build_few_shot_prompt(instruction= current_instruction, examples= examples, user_input= user_input)
            response, chat_session = chat_once(prompt= prompt, provider= provider)
            data = output_validator.extract_structured_data(response_text= response, required_keys= required_keys)

            if data:
                return data

            retries += 1
            if retries < max_retries: 
                current_instruction = self.build_emphasis_instruction(instruction= instruction, required_keys= required_keys, retry= retries)

        return None

if __name__ == "__main__":
    instruction = "Extract the name, date, and amount from the text below into JSON."

    examples = [("Johan paid $50 on March 3rd.", "{\"name\": \"John\", \"date\": \"March 3rd\", \"amount\": 50}"),
                ("Sarah received 120 dollars on July 10.", "{\"name\": \"Sarah\", \"date\": \"July 10\", \"amount\": 120}")]

    user_input = "Mike sent 75 dollars on January 5th."
    required_keys = ["name", "date", "amount"]
    data_provider = RetryExtractor()
    data = data_provider.extract_with_retry(provider= GroqProvider(), instruction= instruction, examples= examples, user_input= user_input, required_keys= required_keys)

    if data:
        print(data)