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
    
    def generate_image_dalle3(
        self,
        prompt: str,
        size: str = "1024x1024",
        response_format: str = "url",
        quality: str = "standard",
        style: str = "vivid",
        n: int = 1,
    ) -> str:
        """
        Generate an image using DALL-E 3.
        Returns the URL to the generated image.
        """
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            response_format=response_format,
            quality=quality,
            style=style,
            n=n
        )
        return response.data[0].url