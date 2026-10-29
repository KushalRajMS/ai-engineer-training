from typing import List
from ai_training.chat.profiles import get_prompt
from ai_training.chat.tokens import ITokenServices
from ai_training.chat.models import Message


class ChatSession:
    def __init__(self, max_history: int = 10, max_pairs: int = 5, system_role_name: str = "default"):
        self.max_history = max_history
        self.max_pairs = max_pairs
        self.messages: List[Message] = []
        self.system_role_name = system_role_name
        self.add_system_message()

    def update_system_prompt(self, profile_name: str) -> None:
        self.system_role_name = profile_name
        content = get_prompt(self.system_role_name)
        self.messages[0] = Message(role= "system", content= content)

    def add_system_message(self):
        content = get_prompt(self.system_role_name)
        self.messages.append(Message(role="system", content= content))

    def add_user_message(self, content: str) -> None:
        if not content or not content.strip():
            raise ValueError("User message cannot be empty.")
        self.messages.append(Message(role="user", content=content.strip()))

    def add_assistant_message(self, content: str) -> None:
        if not content or not content.strip():
            raise ValueError("Assistant message cannot be empty.")
        self.messages.append(Message(role="assistant", content=content.strip()))

    def get_messages(self) -> List[dict]:
        return [message.model_dump() for message in self.messages]

    def time_filter_for_provider(self, message_dict: dict) -> dict :
        return {"role": message_dict["role"], "content": message_dict["content"]}

    def get_windowed_messages(self) -> list[dict]:
        all_messages = self.get_messages()
        windowed_messages= [self.time_filter_for_provider(all_messages[0])] + []

        pairs = 0
        temp_conv = all_messages[::-1]
        fixed_conv = []
        assistant_message= ''
        user_message= ''

        if temp_conv[0]["role"] == "user":
            latest_user_message= self.time_filter_for_provider(temp_conv[0])
            temp_conv.pop(0)
        else:
            latest_user_message = None

        for message in temp_conv:
            if message["role"] == "assistant":
                assistant_message= self.time_filter_for_provider(message)
            if assistant_message and message["role"] == "user":
                user_message= self.time_filter_for_provider(message)
            if pairs < self.max_pairs:
                if user_message:
                    if assistant_message:
                        fixed_conv.append(assistant_message)
                        fixed_conv.append(user_message)
                        pairs += 1
                        if pairs == self.max_pairs : break
                        assistant_message= ''
                        user_message= ''

        windowed_messages += fixed_conv[::-1]

        if latest_user_message:
            windowed_messages.append(latest_user_message)

        return windowed_messages

    def trim_history(self) -> None:
        if len(self.messages) - 1 > self.max_history:
            self.messages = [self.messages[0]] + self.messages[-self.max_history:]

    def clear(self) -> None:
        self.messages = [self.messages[0]] + []

    def estimate_total_tokens(self) -> int:
        token_calculator = ITokenServices()
        estimated_total_tokens = 0
        for message in self.messages:
            estimated_total_tokens += token_calculator.estimate_tokens(message.content)

        return estimated_total_tokens

    def get_metadata_summary(self) -> dict:
        return{
            "mode": self.system_role_name,
            "message_count": len(self.messages),
            "estimated_tokens": self.estimate_total_tokens()
        }

if __name__ == "__main__":
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
    session2.update_system_prompt(profile_name= "code_reviewer")
    print(session2.messages)