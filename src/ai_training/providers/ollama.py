# import httpx
# import json
# from ai_training.providers.base import BaseProvider

# class OllamaProvider(BaseProvider):
#     def __init__(self, model: str = "mistral", base_url: str = "http://localhost:11434"):
#         self.model = model
#         self.base_url = base_url
    
#     def generate(self, messages: list[dict[str, str]]) -> str:
#         try:
#             prompt = ""
#             for message in messages:
#                 role = message.get('role', "").capitalize()
#                 content = message.get('content', "").strip()
#                 prompt += f"{role}: {content}\n"
            
#             response = httpx.post(
#                 f"{self.base_url}/api/generate",
#                 json={
#                     "model": self.model,
#                     "prompt": prompt,
#                     "stream": False
#                 },
#                 timeout=60.0
#             )

#             data = response.json()
#             if "response" not in data:
#                 raise ValueError("Response Field Missing!")
             
#             answer = data.get('response', "").strip()
#             if not answer:
#                 raise ValueError("Ollama returned an empty response.")

#             return answer

#         except httpx.ReadTimeout as exc:
#             raise ValueError("Ollama request timed out") from exc
#         except httpx.ConnectError as exc:
#             raise ValueError("Could not connect to Ollama.") from exc
#         except json.JSONDecodeError as exc:
#             raise ValueError("Received invalid data from Ollama.") from exc
#         except Exception as exc:
#             raise ValueError(f"Error: {exc}")