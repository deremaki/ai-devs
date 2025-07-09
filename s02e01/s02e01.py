import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from llm_client.openai_client import OpenAIClient

AUDIO_DIR = Path("s02e01/przesluchania")
TRANSCRIPTIONS_FILE = Path("s02e01/transkrypcje.txt")
PROMPT_FILE = Path("s02e01/prompt.md")
API_URL = "https://c3ntrala.ag3nts.org/report"
TASK_NAME = "mp3"

def transcribe_audio_files(client):
    print("🔊 Transcribing audio files...")
    transcripts = []
    for file in sorted(AUDIO_DIR.glob("*.m4a")):
        print(f"\t▶ Transcribing {file.name}...")
        with open(file, "rb") as audio_file:
            transcript = client.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            text = transcript.text
        transcripts.append(f"--- {file.name} ---\n" + text.strip())

    full_text = "\n\n".join(transcripts)
    TRANSCRIPTIONS_FILE.write_text(full_text, encoding="utf-8")
    return full_text

def build_prompt(transcripts: str) -> str:
    base_prompt = PROMPT_FILE.read_text(encoding="utf-8")
    return f"{base_prompt}\n\nTRANSKRYPCJE:\n{transcripts}"

def send_answer_to_centrala(api_key: str, answer: str):
    print("📡 Sending answer to Centrala...")
    response = requests.post(API_URL, json={
        "task": TASK_NAME,
        "apikey": api_key,
        "answer": answer
    })
    print("📬 Response from Centrala:")
    print(response.text)

def run_task():  # patched to use OpenAIClient
    load_dotenv()
    api_key = os.getenv("C3NTRALA_API_KEY")
    if not api_key:
        raise RuntimeError("Brak API_KEY w .env")

    llm = OpenAIClient()
    if TRANSCRIPTIONS_FILE.exists():
        print("📄 Found existing transcription file. Skipping Whisper step.")
        transcripts = TRANSCRIPTIONS_FILE.read_text(encoding="utf-8")
    else:
        transcripts = transcribe_audio_files(llm)
    full_prompt = build_prompt(transcripts)
    raw_answer = llm.chat(
        user_message=full_prompt,
        system_prompt="Jesteś pomocnym agentem analizującym przesłuchania."
    )
    print("Odpowiedź LLM:", raw_answer)

    answer = "".join([line.replace("Odpowiedź:", "").strip() for line in raw_answer.splitlines() if line.strip().startswith("Odpowiedź:")])
    print("Odpowiedź:", answer)

    send_answer_to_centrala(api_key, answer)