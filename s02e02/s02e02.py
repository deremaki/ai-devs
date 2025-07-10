import base64
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def run_task():
    load_dotenv()
    client = OpenAIClient()

    image_dir = Path("s02e02")
    image_paths = sorted(image_dir.glob("map*.png"))
    if len(image_paths) != 4:
        raise ValueError("Expected exactly 4 map images named map1.png to map4.png")

    encoded_images = [encode_image(str(p)) for p in image_paths]

    messages = [
        {"role": "system", "content": "You are an expert at recognizing Polish cities based on map fragments."},
        {"role": "user", "content": [
            {
                "type": "text",
                "text": (
                    "Three of these four map fragments are from the same Polish city. "
                    "One is from a different city. Identify which one is different (by filename) "
                    "and what city the three matching ones belong to. "
                    "Respond in JSON: {\\\"miasto\\\": \\\"...\\\", \\\"inny\\\": \\\"mapX.png\\\"}."
                )
            }
        ] + [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img}"}}
            for img in encoded_images
        ]}
    ]

    content = client.vision_chat(messages=messages, model="gpt-4o", max_tokens=300)


    print(content)