from ai_training.providers.mock import MockProvider
from ai_training.providers.groq import GroqProvider
from ai_training.chat.session import ChatSession
from ai_training.chat.chatbot import chat_once
import json
from datetime import datetime
import os

def main() -> None:
    while True:
        provider_name = input("Choose provider (mock/groq): ").strip().lower()

        if provider_name == "mock":
            provider = MockProvider()
            break
        if provider_name == "groq":
            provider = GroqProvider()
            break

    user_preferred_role = input("Chose role (technical_writer/data_analyst/code_reviewer/default: )")
    chat_session = ChatSession(system_role_name= user_preferred_role.strip().lower())
    while True:
        user_input = input("You: ").strip()

        if user_input in ("exit", "quit"):
            break

        try:
            response, chat_session = chat_once(
                prompt= user_input, 
                provider= provider, 
                chat_session= chat_session
            )
        except ValueError as exc:
            print(f"Error: {exc}")
            continue

        print(f"Assistant: {response}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("artifacts", exist_ok=True)
    file_path = f"artifacts/chat_history_{timestamp}.json"

    with open(file_path, "w") as file:
        json.dump(chat_session.get_messages(), file, indent= 2)


if __name__ == "__main__":
    main()