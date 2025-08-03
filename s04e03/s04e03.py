import os
import requests
import html2text
from urllib.parse import urljoin, urlparse

from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

from bs4 import BeautifulSoup

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "softo"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

BASE_URL = "https://softo.ag3nts.org"
QUESTIONS_URL = f"https://c3ntrala.ag3nts.org/data/{API_KEY}/softo.json"
MAX_DEPTH = 10


llm = OpenAIClient()


html_converter = html2text.HTML2Text()
html_converter.ignore_links = False
html_converter.ignore_images = True
html_converter.ignore_emphasis = True
html_converter.skip_internal_links = True
html_converter.ignore_anchors = True
html_converter.body_width = 0


def clean_html(html):
    soup = BeautifulSoup(html, "html.parser")

    # Usuń komentarze
    for comment in soup.find_all(string=lambda text: isinstance(text, type(soup.comment))):
        comment.extract()

    # Usuń elementy z klasą "hidden"
    for hidden in soup.select(".hidden"):
        hidden.decompose()

    return str(soup)


def fetch_markdown(url):
    try:
        print(f"[FETCH] URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        cleaned_html = clean_html(response.text)
        markdown = html_converter.handle(cleaned_html)
        print(f"[FETCH] Pobrano i skonwertowano stronę ({len(markdown)} znaków)")
        return markdown
    except Exception as e:
        print(f"[ERROR] Nie udało się pobrać {url}: {e}")
        return ""


def ask_if_answer_present(content, question):
    print(f"[LLM] Sprawdzam, czy jest odpowiedź na pytanie: {question}")
    prompt = f"""
Na podstawie poniższej treści strony internetowej:

---
{content}
---

Czy można udzielić odpowiedzi na pytanie: \"{question}\"?

Udziel zwięzłej i bezpośredniej odpowiedzi na pytanie ALBO napisz NIE
"""
    response = llm.chat(prompt)
    print(f"[LLM] Odpowiedź na obecność odpowiedzi: {response.strip()}")
    return response.strip()


def ask_if_answer_present(content, question):
    print(f"[LLM] Sprawdzam, czy jest odpowiedź na pytanie: {question}")
    prompt = f"""
Na podstawie poniższej treści strony internetowej:

---
{content}
---

Czy można udzielić odpowiedzi na pytanie: \"{question}\"? Musisz być pewny ze da się odpowiedziec konkretnie na pytanie, jeśli nie jesteś pewny odpowiedz nie.

Jeśli tak, zwróć wyłącznie konkretną, zwięzłą odpowiedź, np. adres, url, wartosc, etc.  — bez żadnego komentarza ani wstępu.
Jeśli nie, napisz dokładnie tylko: NIE
"""
    response = llm.chat(prompt)
    print(f"[LLM] Odpowiedź na obecność odpowiedzi: {response.strip()}")
    return response.strip()


def ask_which_link_to_follow(content, question, visited):
    print(f"[LLM] Pytam, które linki są warte sprawdzenia dla pytania: {question}")
    prompt = f"""
Na podstawie poniższej treści strony internetowej:

---
{content}
---

Wybierz 3 do 5 linków (href), które najprawdopodobniej prowadzą do odpowiedzi na pytanie: \"{question}\". Posiłkuj się tekstem wokół linku. Jesli nie widzisz oczywistej odpowiedzi rozwaz rzeczy typu "portfolio" albo "aktualnosci" - tam tez mogą być informacje.
Zwróć je w postaci listy adresów URL (href), każdy w osobnej linii. Nie dodawaj tekstu opisu ani żadnych znaków przed/po linkach.
"""
    response = llm.chat(prompt)
    candidates = [line.strip() for line in response.splitlines() if line.strip()]
    print(f"[LLM] Kandydaci na linki: {candidates}")
    for link in candidates:
        resolved = urljoin(BASE_URL, link)
        if resolved not in visited:
            print(f"[LLM] Wybrano nieodwiedzony link: {resolved}")
            return resolved
    print("[LLM] Wszystkie kandydaty były już odwiedzone")
    return None


def resolve_link(base, link):
    resolved = urljoin(base, link)
    print(f"[LINK] Rozwiązano link: {link} -> {resolved}")
    return resolved


def search_for_answer(start_url, question):
    visited = set()
    to_visit = [(start_url, 0)]

    while to_visit:
        current_url, depth = to_visit.pop(0)
        print(f"[NAV] Odwiedzam: {current_url} | Głębokość: {depth}")

        if current_url in visited:
            print(f"[NAV] URL już odwiedzony, pomijam: {current_url}")
            continue

        if depth > MAX_DEPTH:
            print(f"[NAV] Przekroczono maksymalną głębokość dla: {current_url}")
            continue

        visited.add(current_url)
        content = fetch_markdown(current_url)
        if not content:
            continue

        answer = ask_if_answer_present(content, question)
        if not answer.strip().upper().startswith("NIE"):
            final = answer.replace("TAK", "").strip()
            print(f"[FOUND] Znaleziono odpowiedź: {final}")
            return final

        next_link = ask_which_link_to_follow(content, question, visited)
        if next_link:
            next_url = resolve_link(current_url, next_link)
            to_visit.append((next_url, depth + 1))
        else:
            print(f"[NAV] LLM nie wskazał kolejnego linku z {current_url}")

    print("[FAIL] Nie znaleziono odpowiedzi.")
    return "NIE ZNALEZIONO"


def run_task():
    print("[START] Pobieram pytania...")
    response = requests.get(QUESTIONS_URL)
    questions = response.json()
    print(f"[START] Pobrano pytania: {list(questions.keys())}")

    answers = {}
    for key, question in questions.items():
        print(f"\n[QUESTION {key}] {question}")
        answer = search_for_answer(BASE_URL, question)
        print(f"[ANSWER {key}] {answer}")
        answers[key] = answer

    result = {
        "task": "softo",
        "apikey": API_KEY,
        "answer": answers
    }

    sender.send(answers)