import os
from openai import OpenAI
from typing import List, Optional, Dict
from .base import LLMClient

class OpenAIClient(LLMClient):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        self.client = OpenAI(api_key=self.api_key)

    def chat(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = "gpt-4.1-nano",
        extra_context: Optional[List[Dict]] = None,
    ) -> str:
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if extra_context:
            messages.extend(extra_context)

        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )

        return response.choices[0].message.content.strip()
    
    def vision_chat(
        self,
        messages: List[Dict],
        model: str = "gpt-4o",
        max_tokens: int = 500,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()