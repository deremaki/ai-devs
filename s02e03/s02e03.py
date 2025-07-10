import os
import requests
from typing import Optional

from llm_client.openai_client import OpenAIClient

TASK_NAME = "robotid"

def get_robot_description(api_key: str) -> str:
    """
    Pobiera opis robota z serwera Centrali.
    """
    url = f"https://c3ntrala.ag3nts.org/data/{api_key}/{TASK_NAME}.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()["description"]

def submit_image_url(api_key: str, image_url: str) -> None:
    """
    Wysyła link do wygenerowanego obrazu do Centrali.
    """
    payload = {
        "task": TASK_NAME,
        "apikey": api_key,
        "answer": image_url
    }
    response = requests.post("https://c3ntrala.ag3nts.org/report", json=payload)
    response.raise_for_status()
    print("✅ Odpowiedź przesłana poprawnie:", response.text)

def run_task(api_key: Optional[str] = None) -> None:
    """
    Główna funkcja uruchamiająca zadanie.
    """
    api_key = api_key or os.getenv("C3NTRALA_API_KEY")
    if not api_key:
        raise ValueError("Brak klucza API. Dodaj go do zmiennej środowiskowej C3NTRALA_API_KEY.")

    print("📥 Pobieranie opisu robota...")
    description = get_robot_description(api_key)
    print("📜 Opis robota:", description)

    print("🎨 Generowanie obrazu robota...")
    client = OpenAIClient()
    image_url = client.generate_image_dalle3(prompt=description)
    print("🖼️ Obraz wygenerowany:", image_url)

    print("📡 Wysyłanie odpowiedzi do Centrali...")
    submit_image_url(api_key, image_url)
