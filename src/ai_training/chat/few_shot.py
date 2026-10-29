from ai_training.chat.chatbot import chat_once

class FewShot:
    def build_few_shot_prompt(self, instruction: str = None, examples: list[tuple[str, str]] = None, user_input: str = None):
        if instruction and examples:
            example_text= f"{instruction}\n"

            for i, example in enumerate(examples, start= 1):
                example_text += f"\nExample {i}:\nInput: {example[0]}\nOutput: {example[1]}\n\n"

            example_text +=f"Now do the same for this Input:\nInput: {user_input}\nOutput: "

            return example_text

        elif instruction:
            return (f"{instruction}\n\nGive me the Output based on the given instruction above:\nInput: {user_input}\nOutput: ")

        elif examples:
            example_text= ""
            for i, example in enumerate(examples, start= 1):
                example_text += f"Example {i}:\nInput: {example[0]}\nOutput: {example[1]}\n\n"
            example_text +=f"\nGive me Output for below Input based on the above examples:\nInput: {user_input}\nOutput: "

            return example_text

        return user_input