from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator


class BaseProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        Accepts chat messages and returns a text response.
        """
        pass

    @abstractmethod
    def generate_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        pass