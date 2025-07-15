# s02e05/s02e05.py
import os
import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urljoin
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient
import base64

TASK_NAME = "arxiv"
BASE_URL = "https://c3ntrala.ag3nts.org"
ARTICLE_URL = f"{BASE_URL}/dane/arxiv-draft.html"
QUESTIONS_URL_TEMPLATE = f"{BASE_URL}/data/{{apikey}}/arxiv.txt"
CACHE_DIR = Path("s02e05/cache")
OUTPUT_MD_PATH = CACHE_DIR / "context.md"
ARTICLE_PATH = Path("s02e05/article.html")
QUESTIONS_PATH = Path("s02e05/questions.txt")
IMAGES_DIR = Path("s02e05/media/images")
AUDIOS_DIR = Path("s02e05/media/audio")

load_dotenv()
C3_API_KEY = os.getenv("C3NTRALA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm = OpenAIClient()
CACHE_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AUDIOS_DIR.mkdir(parents=True, exist_ok=True)

def download_file(url: str, save_path: Path):
    r = requests.get(url)
    save_path.write_bytes(r.content)


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Usuwamy skrypty i style
    for tag in soup(["script", "style"]):
        tag.decompose()

    lines = []

    for el in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p"]):
        if el.name == "p" and el.has_attr("data-wtf"):
            continue  # pomijamy specjalne tagi

        text = el.get_text(strip=True)
        if not text:
            continue

        if el.name.startswith("h"):
            level = int(el.name[1])
            lines.append(f"{'#' * level} {text}")
        elif el.name == "p":
            lines.append(text)

    return "\n".join(lines)

def extract_media_urls(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    images = [urljoin(ARTICLE_URL, img["src"]) for img in soup.find_all("img") if img.get("src")]
    audios = [urljoin(ARTICLE_URL, audio["href"]) for audio in soup.find_all("a") if audio.get("href") and audio.get("href").endswith(".mp3")]
    return {"images": images, "audios": audios}

def describe_image(img_path: Path, context: str, caption: str = "") -> str:
    with open(img_path, "rb") as f:
        b64_img = base64.b64encode(f.read()).decode("utf-8")

    text_parts = []
    if caption:
        text_parts.append(f"Podpis pod obrazkiem: {caption}")
    text_parts.append("Opisz obrazek dwoma zdaniami. Pierwsze zdanie powinno być krótkie i dokładnie opisujące co widzimy na obrazku (np. nazwę dania, nazwe zwierzecia, dokładna nazwa miejsca, nazwa miasta gdzie znajduje sie miejsce itp.), drugie zdanie powinno być dłuższe i opisujące obrazek w kontekście artykułu i podpisu pod obrazkiem.")
    text_parts.append("Kontekst artykułu:\n" + context)
    
    return llm.vision_chat(
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "\n\n".join(text_parts)},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
            ]},
        ],
        max_tokens=2000
    )
def process_images(html: str, article_context: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    out = []

    for figure in soup.find_all("figure"):
        img = figure.find("img")
        if not img or not img.get("src"):
            continue

        img_url = urljoin(ARTICLE_URL, img["src"])
        img_name = os.path.basename(img["src"])
        img_path = IMAGES_DIR / img_name

        # Zachowujemy obrazek
        if not img_path.exists():
            download_file(img_url, img_path)

        # Podpis pod obrazkiem
        caption = ""
        figcaption = figure.find("figcaption")
        if figcaption:
            caption = figcaption.get_text(strip=True)

        print("Processing image: ", img_name)

        # Opis obrazka z kontekstem
        description = describe_image(img_path, context=article_context, caption=caption)

        print("Description: ", description)

        out.append(f"### Obrazek: {img_name}\n{description}\n")

    return "\n".join(out)

def process_audios(audio_urls: list) -> str:
    out = []
    for i, url in enumerate(audio_urls):
        path = AUDIOS_DIR / f"audio_{i}.mp3"
        if not path.exists():
            download_file(url, path)
        print("Processing audio: ", str(path))
        transcript = llm.transcribe_with_whisper(str(path))
        print("Transcript: ", transcript)
        out.append(f"### Transkrypcja nagrania {i+1}\n{transcript}\n")
    return "\n".join(out)

def get_questions(api_key: str) -> dict:
    url = QUESTIONS_URL_TEMPLATE.format(apikey=api_key)
    response = requests.get(url)
    QUESTIONS_PATH.write_text(response.text)

    questions = {}
    for line in response.text.strip().splitlines():
        if "=" in line:
            qid, text = line.split("=", 1)
            questions[qid.strip()] = text.strip()

    return questions

def answer_questions(questions: dict, context: str) -> dict:
    system_prompt = "Na podstawie poniższego kontekstu odpowiedz na każde pytanie JEDNYM krótkim zdaniem. Format odpowiedzi: Odpowiedź: <jedno zdanie>."
    answers = {}

    for qid, question in questions.items():
        user_prompt = f"Kontekst:\n{context}\n\nPytanie: {question}"
        print("Question: ", question)
        response = llm.chat(user_message=user_prompt, system_prompt=system_prompt)

        # Szukamy odpowiedzi w formacie "Odpowiedź: ..."
        match = re.search(r"Odpowied[zź]:\s*(.+)", response, re.IGNORECASE)
        if match:
            answers[qid] = match.group(1).strip()
        else:
            answers[qid] = response.strip()  # fallback – cała odpowiedź
        print("Answer: ", answers[qid])

    return answers

def run_task():
    print("Pobieranie artykułu...")
    html = requests.get(ARTICLE_URL).text
    ARTICLE_PATH.write_text(html)
    text = extract_text_from_html(html)
    media = extract_media_urls(html)

    print("Przetwarzanie obrazów...")
    img_descriptions = process_images(html, article_context=text)

    print("Przetwarzanie audio...")
    audio_transcripts = process_audios(media["audios"])

    print("Scalanie kontekstu...")
    full_context = f"## Tekst artykułu\n{text}\n\n## Obrazy\n{img_descriptions}\n\n## Transkrypcje\n{audio_transcripts}"
    OUTPUT_MD_PATH.write_text(full_context)

    print("Pobieranie pytań...")
    questions = get_questions(C3_API_KEY)

    print("Generowanie odpowiedzi...")
    answers = answer_questions(questions, full_context)

    out_json = {
        "task": TASK_NAME,
        "apikey": C3_API_KEY,
        "answer": answers
    }

    print("\n--- ODPOWIEDŹ JSON ---")
    import json
    print(json.dumps(out_json, indent=2, ensure_ascii=False))

    print("Wysyłanie odpowiedzi do centrali...")
    submit_url = f"{BASE_URL}/report"
    response = requests.post(submit_url, json=out_json)
    print("Odpowiedź centrali:", response.text)


    correct_out_json = {
        "task": TASK_NAME,
        "apikey": C3_API_KEY,
        "answer": {
            "01": "Użyto owocu w postaci truskawki.",
            "02": "Na rynku w Krakowie.",
            "03": "Bomba chciał znaleźć hotel w Grudziądzu.",
            "04": "Resztki pizzy z ananasem.",
            "05": "Od tytułu powieści \"Brave New World\"."
        }
    }
