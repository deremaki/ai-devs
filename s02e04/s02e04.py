import os
import json
import requests
import base64
from pathlib import Path
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient

load_dotenv()

client = OpenAIClient()

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def categorize(text: str) -> str:
    prompt = (
        "Na podstawie treści zdecyduj, czy zawiera informacje o schwytanych ludziach "
        "lub śladach ich obecności (kategoria: people), o naprawach usterek hardwarowych (kategoria: hardware), "
        "czy o czymś innym (kategoria: none). Jak nie jesteś pewny, odpowiedz none. Odpowiedz tylko jedną z tych kategorii: people, hardware, none.\n\n"
        f"NOTATKA:\n{text}"
    )
    return client.chat(prompt).strip().lower()

def run_task():
    base_dir = Path("s02e04/pliki_z_fabryki")
    files = list(base_dir.glob("**/*"))

    result = {
        "people": [],
        "hardware": []
    }

    for file in files:
        if "facts" in file.parts:
            continue
        if file.is_dir():
            continue
        if file.suffix == "":
            continue

        try:
            if file.suffix == ".txt":
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                category = categorize(content)
                print(file.name + ": " + category)

            elif file.suffix == ".png":
                messages = [
                    {
                        "role": "system",
                        "content": "Na podstawie zawartości obrazka zdecyduj, czy zawiera informacje o schwytanych ludziach (people), naprawach hardware'u (hardware) - hardware'u nie software'u!, czy nic z tego (none). Odpowiedz tylko jedną z tych kategorii: people, hardware, none."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(file)}"}}
                        ]
                    }
                ]
                response = client.vision_chat(messages)
                category = response.strip().lower()
                print(file.name + ": " + category)

            elif file.suffix == ".mp3":
                transcript = client.transcribe_with_whisper(str(file))
                category = categorize(transcript)
                print(file.name + ": " + category)

            else:
                continue

            if category == "people":
                result["people"].append(file.name)
            elif category == "hardware":
                result["hardware"].append(file.name)

        except Exception as e:
            print(f"❌ Błąd przy pliku {file.name}: {e}")

    # sortowanie nazw plików
    result["people"].sort()
    result["hardware"].sort()

    final_json = {
        "task": "kategorie",
        "apikey": os.getenv("C3NTRALA_API_KEY"),
        "answer": result
    }

    print(final_json)

    # wysyłka do centrali

    response = requests.post(
        "https://c3ntrala.ag3nts.org/report",
        json=final_json
    )
    print("✅ Centrala odpowiedziała:", response.status_code)
    print(response.text)