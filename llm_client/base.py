from abc import ABC, abstractmethod
from typing import List, Optional, Dict

class LLMClient(ABC):
    @abstractmethod
    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        extra_context: Optional[List[Dict]] = None,
    ) -> str:
        """Send a chat message to the LLM and return its response."""
        pass