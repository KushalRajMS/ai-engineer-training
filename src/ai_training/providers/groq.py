from __future__ import annotations
import os
import httpx
import json
from dotenv import load_dotenv
from ai_training.providers.base import BaseProvider
from typing import Generator

class GroqProvider(BaseProvider):
    def __init__(self, model: str = "openai/gpt-oss-20b", api_key: str | None = None):
        if not api_key:
            load_dotenv()
            api_key= os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("Missing Key: Please set the API Key")

        self.model = model
        self.api_key = api_key
        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, messages: list[dict[str, str]]) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }

        try:
            response= httpx.post(
                url= self.url,
                headers= headers,
                json= payload,
                timeout=60.0,
            )

            if response.status_code != 200:
                raise ValueError(f"Groq API Error ({response.status_code}): {response.text}")

            data = response.json()
            content= data["choices"][0]["message"]["content"]

            if not content:
                raise ValueError("Groq returned empty response.")
            return content
        except httpx.ReadTimeout as exc:
            raise ValueError("Groq request timed out") from exc
        except httpx.ConnectError as exc:
            raise ValueError("Could not connect to Groq") from exc
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            raise ValueError("Unexpected response shape from Groq") from exc
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Error: {exc}") from exc

    def generate_stream(self, messages: list[dict[str, str]]) -> Generator[str, None, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }
        try:
            yielded = False
            with httpx.stream("POST", url= self.url, headers= headers, json= payload, timeout=60) as response:
                for line in response.iter_lines():
                    if line:
                        cleaned_line = line.removeprefix("data: ")
                        if cleaned_line != "[DONE]":
                            try:
                                data = json.loads(cleaned_line)
                            except json.JSONDecodeError:
                                continue
                            content = data["choices"][0]["delta"].get("content")
                            if content != "":
                                yield content
                                yielded = True
            if not yielded:
                raise ValueError("Groq returned empty response.")
        except httpx.ReadTimeout as exc:
            raise ValueError("Groq request timed out.") from exc
        except httpx.ConnectError as exc:
            raise ValueError("Couldn't connect to Groq.") from exc
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            raise ValueError("Unexpected response shape from Groq.") from exc
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError(f"Error: {exc}") from exc

if __name__ == "__main__":
    provider = GroqProvider()
    messages = [
        {"role": "system", "content": "You are a useful assistant."},
        {"role": "user", "content": "Say hello in one sentence."}
    ]
    print(provider.generate(messages))