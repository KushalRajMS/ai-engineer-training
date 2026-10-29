from ai_training.providers.mock import MockProvider
from ai_training.chat.session import ChatSession
from ai_training.providers.groq import GroqProvider

def chat_once(prompt, provider=None, chat_session=None):
    if prompt.strip() == "":
        raise ValueError("Prompt cannot be empty.")

    if provider is None:
        provider = MockProvider()

    if chat_session is None:
        chat_session = ChatSession()

    chat_session.add_user_message(prompt)
    messages = chat_session.get_windowed_messages()
    response = provider.generate(messages)

    if not response or not response.strip():
        raise ValueError("Provider returned an empty response.")

    chat_session.add_assistant_message(response)
    chat_session.trim_history()
    return response, chat_session

class ChatBot:
    def __init__(self, provider, profile: str = "default", max_history: int = 10, max_pairs: int = 5):
        self.provider = provider
        self.session = ChatSession(max_history= max_history, max_pairs= max_pairs, system_role_name= profile)

    def send_message(self, prompt: str) -> str:
        response, self.session = chat_once(prompt= prompt, provider= self.provider, chat_session= self.session)
        return response

    def get_history(self) -> list[dict]:
        return (self.session.get_messages())

    def clear_memory(self) -> None:
        self.session.clear()

    def switch_provider(self, provider) -> None:
        self.provider = provider

    def set_prompt_mode(self, profile: str) -> None:
        self.session.update_system_prompt(profile_name= profile)

    def stream_message(self, prompt: str):
        if prompt.strip() == "":
            raise ValueError("Prompt cannot be empty.")
        self.session.add_user_message(content=prompt)
        response = ""
        messages = self.session.get_windowed_messages()
        stream = self.provider.generate_stream(messages)
        for chunk in stream:
            if chunk:
                response += chunk
                yield chunk
        if not response or not response.strip():
            raise ValueError("Provider returned an empty response.")
        self.session.add_assistant_message(content=response)
        self.session.trim_history()

if __name__ == "__main__":
    chat = ChatBot(provider= GroqProvider())
    print(chat.send_message("hello"))