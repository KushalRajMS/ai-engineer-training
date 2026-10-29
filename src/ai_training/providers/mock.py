from typing import List, Dict, Generator
from ai_training.providers.base import BaseProvider


class MockProvider(BaseProvider):
    def generate(self, messages: List[Dict[str, str]]) -> str:
        user_text = ""
        for message in messages:
            if message.get("role") == "user":
                user_text = message.get("content", "").strip()

        if not user_text:
            return "Mock provider: empty input received."

        return (
            f"Mock response for: '{user_text}'\n"
            f"Model: mock-model\n"
            f"Status: success"
        )

    def generate_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        response = self.generate(messages= messages)
        chunk_size = 8
        chunk = ""
        for char in response:
            chunk += char
            if len(chunk) == chunk_size:
                yield chunk
                chunk = ""
        if chunk:
            yield chunk