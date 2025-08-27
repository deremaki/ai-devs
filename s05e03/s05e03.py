import os
import requests
import json

from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient

from concurrent.futures import ThreadPoolExecutor
from time import perf_counter

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "notes"

llm = OpenAIClient()

RAFAL_URL = "https://rafal.ag3nts.org/b46c3"
PASSWORD = "NONOMNISMORIAR"

def _get_json(url: str):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def _ask_llm(prompt: str):
    # krótko, po polsku – minimalny narzut
    answer = llm.chat(
        system_prompt="Odpowiadaj zwięźle, po polsku, niepełnym zdaniem",
        user_message=prompt
    ).strip()
    print(answer)
    return answer


def run_task():

    t0 = perf_counter()

    # 1. + 2.  wyślij hasło
    r = requests.post(RAFAL_URL, json={"password": PASSWORD})
    r.raise_for_status()
    hash_value = r.json().get("message")
    print(f"[{perf_counter()-t0:.3f}s] Hasło -> hash")

    # 3. i 4. wyślij hash w polu "sign"
    r = requests.post(RAFAL_URL, json={"sign": hash_value})
    r.raise_for_status()
    signed = r.json()
    timestamp = signed.get("message").get("timestamp")
    signature = signed.get("message").get("signature")
    urls = signed.get("message").get("challenges", [])
    print(urls[0])
    print(urls[1])
    print(f"[{perf_counter()-t0:.3f}s] Hash -> timestamp/signature")

    # 5. przeczytaj pytania
    with ThreadPoolExecutor(max_workers=2) as ex:
        s0_future = ex.submit(_get_json, "https://rafal.ag3nts.org/source0")
        s1_future = ex.submit(_get_json, "https://rafal.ag3nts.org/source1")
    s0, s1 = s0_future.result(), s1_future.result()
    print("S0:", s0.get("data")); print("S1:", s1.get("data"))
    print(f"[{perf_counter()-t0:.3f}s] Pobranie source0/source1")


    ARTICLE = ""
    try:
        with open("s05e03/article.md", "r", encoding="utf-8") as f:
            ARTICLE = f.read()
    except FileNotFoundError:
        ARTICLE = ""

    #prep questions
    school_qs = s0.get("data", [])[:4]
    article_qs = s1.get("data", [])[:2]

    #prep prompts
    p_school = [f"Odpowiedz krótko na pytanie z wiedzy szkolnej: {q}" for q in school_qs]
    p_article = [f"Na podstawie poniższego tekstu odpowiedz krótko: {q}\n\n---\n{ARTICLE}"
                 for q in article_qs]
    
    prompts = p_school + p_article

    with ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(_ask_llm, prompts))
    print(f"[{perf_counter()-t0:.3f}s] LLM odpowiedzi gotowe")


    answer = results

    final_answer = {
        "apikey":API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "answer": answer
    }
    print(json.dumps(final_answer, indent=2, ensure_ascii=False))
    print(f"[{perf_counter()-t0:.3f}s] Gotowe do wysyłki")

    final_resp = requests.post(RAFAL_URL, json=final_answer)
    print(f"[{perf_counter()-t0:.3f}s] Zgłoszenie zakończone:", final_resp.text)