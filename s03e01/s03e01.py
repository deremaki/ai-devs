import os
import json
import requests
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient

REPORTS_DIR = os.path.join("s03e01", "pliki_z_fabryki")
FACTS_DIR = os.path.join(REPORTS_DIR, "facts")
PROMPT_FILE = os.path.join("s03e01", "prompt.md")
CONTEXT_FILE = os.path.join("s03e01", "context.txt")
API_ENDPOINT = "https://c3ntrala.ag3nts.org/report"


def load_prompt() -> str:
    with open(PROMPT_FILE, encoding="utf-8") as f:
        return f.read()


def build_context_from_facts() -> str:
    all_facts = []
    for filename in os.listdir(FACTS_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(FACTS_DIR, filename)
            with open(path, encoding="utf-8") as f:
                all_facts.append(f.read().strip())
    context = "\n\n".join(all_facts)
    with open(CONTEXT_FILE, "w", encoding="utf-8") as f:
        f.write(context)
    return context

def extract_keywords(response: str) -> str:
    lines = response.strip().splitlines()
    for line in reversed(lines):
        if line.lower().startswith("odpowiedź:"):
            return line.split("Odpowiedź:", 1)[-1].strip()
    return ""


def run_task():
    client = OpenAIClient()
    api_key = os.getenv("C3NTRALA_API_KEY")
    prompt = load_prompt()
    context = build_context_from_facts()

    answer = {}

    for filename in os.listdir(REPORTS_DIR):
        full_path = os.path.join(REPORTS_DIR, filename)
        if filename.endswith(".txt") and os.path.isfile(full_path) and filename != "context.txt" and not filename.startswith("facts"):
            with open(full_path, encoding="utf-8") as f:
                report_text = f.read().strip()

            print("Processing file: " + filename)
            user_message = f"Oto kontekst: {context} \n\nOto plik tekstowy: {report_text}\n\nPodaj listę słów kluczowych dla pliku o nazwie: {filename}"
            raw_response = client.chat(user_message=user_message, system_prompt=prompt, model= "gpt-4.1-mini")
            print(raw_response)
            keywords = extract_keywords(raw_response + "\n\n")
            answer[filename] = keywords
            print("KEYWORDS: " + keywords + "\n\n\n")

    payload = {
        "task": "dokumenty",
        "apikey": api_key,
        "answer": answer
    }

    print("\n--- ODPOWIEDŹ JSON ---")
    import json
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    response = requests.post(API_ENDPOINT, json=payload)
    print("Odpowiedź z serwera:")
    print(response.status_code)
    print(response.text)
