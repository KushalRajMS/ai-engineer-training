from ai_training.chat.chatbot import chat_once

class Summarizer:
    def build_summary_prompt(self, content: str, style: str = "brief") -> str:
        if style == "brief":
            return(f"Summarize the following text in 2-3 sentences:\n\n{content}")
        elif style == "detailed":
            return(f"Summarize the following text thorough and covering all the key points:\n\n{content}")
        elif style == "bullets":
            return(f"Summarize the following text in bullet points:\n\n{content}")
        return(f"Summarize the following text in 2-3 sentences:\n\n{content}")
        

    def summarize_file(self, file_dict: dict, provider, style: str = "brief") ->dict:
        try:
            prompt = self.build_summary_prompt(str(file_dict.get("content", "")), style=style)
            response, chat_history = chat_once(prompt= prompt, provider= provider)
        except ValueError:
            return {"filename": file_dict.get("filename", "Unknown"),
                    "summary": None,
                    "success": False
                }
        return {
            "filename": file_dict.get("filename", "Unknown"),
            "summary": response,
            "success": True
        }

    def summarize_batch(self, files: list[dict], provider, style: str = "brief") -> list[dict]:
        summarized_files: list[dict] = []
        for data in files:
            try:
                response = self.summarize_file(file_dict= data, provider= provider, style= style)
                summarized_files.append(response)
            except Exception:
                summarized_files.append({
                    "filename": data.get("filename", "Unknown"),
                    "summary": None,
                    "success": False
                })
        return summarized_files