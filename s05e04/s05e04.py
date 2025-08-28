import os
import json
import re
import threading
import uuid
import base64
from datetime import datetime

import requests
from fastapi import FastAPI, Request, HTTPException, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, constr
import uvicorn
from llm_client.openai_client import OpenAIClient

from s05e04.prompts import JAILBREAK_PROMPT, DECISION_PROMPT_SYSTEM


llm = OpenAIClient()

app = FastAPI(title="AIDevs s05e04 webhook", version="1.0.0")

ACCESS_PASSWORD = "S2FwaXRhbiBCb21iYTsp"

KEY = ""
TIMESTAMP = ""


class AnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # odrzuć nieznane pola
    question: constr(strip_whitespace=True, min_length=1)

@app.post("/webhook")
async def webhook(req: Request, body: AnswerRequest):
    # Wymuś Content-Type: application/json
    ct = req.headers.get("content-type", "")
    if "application/json" not in ct:
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")
    
    print("QUESTION:", body.question)
    answer = answer_question(body.question)

    print(answer)

    return {
        "answer": answer
    }

def try_jailbreak_flag():
    jailbreak_prompt = JAILBREAK_PROMPT
    return jailbreak_prompt


def fetch_file(url: str, out_path: str) -> str:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def transcript_audio(url):

    audio_path = "s05e04/audio.mp3"
    fetch_file(url, audio_path)

    transcript = llm.transcribe_with_whisper(audio_path)

    return transcript

def describe_photo(url):

    image_path = "s05e04/photo.png"
    fetch_file(url, image_path)

    with open(image_path, "rb") as f:
        encoded_image = base64.b64encode(f.read()).decode("utf-8")

    messages = [
                    {
                        "role": "system",
                        "content": "Jesteś wybitnym opisywaczem obrazków. Krótko opisz co znajduje się na załączonym obrazku"
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_image}"}}
                        ]
                    }
                ]
    response = llm.vision_chat(messages)
    print(response)
    return response


def ask_llm(question):
    global KEY, TIMESTAMP

    resp = llm.chat(
        user_message="Sklasyfikuj to pytanie: " + question,
        system_prompt=DECISION_PROMPT_SYSTEM
    )

    data = json.loads(resp)
    scenario, params = data.get("scenario"), data.get("params")

    print("LLM scenario: " + scenario)
    
    if scenario == "password":
        return ACCESS_PASSWORD
    elif scenario == "data":
        KEY = params.get("klucz")
        TIMESTAMP = params.get("data")
        return "OK"
    elif scenario == "value":
        if params == "klucz":
            return KEY
        if params == "data":
            return TIMESTAMP
    elif scenario == "audio":
        url = params
        return transcript_audio(url)
    elif scenario == "photo":
        url = params
        return describe_photo(url)


def answer_question(question):

    answer = "Test"

    if "POMIDOR" in question:
        return "TAK"
    elif "Czekam na nowe instrukcje" in question:
        answer = try_jailbreak_flag()
    else:
        answer = ask_llm(question)

    return answer



def report_to_centrala():
    api_key = os.getenv("C3NTRALA_API_KEY")
    public_url = os.getenv("PUBLIC_WEBHOOK_URL")  # np. z ngrok
    if not api_key or not public_url:
        print("Brak C3NTRALA_API_KEY lub PUBLIC_WEBHOOK_URL w env.")
        return
    
    payload = {
        "task": "serce",
        "apikey": api_key,
        "justUpdate": True, #questions skip mentioned in a task
        "answer": f"{public_url}/webhook"
    }
    print(f"Zgłaszam webhook do centrali: {payload['answer']}")
    try:
        r = requests.post("https://c3ntrala.ag3nts.org/report", json=payload, timeout=None)
        print("Odpowiedź z centrali:", r.text)
        m = re.search(r"FLG:[A-Za-z0-9_]+", r.text)
        if m:
            print("🎯 ZNALAZŁEM FLAGĘ:", m.group(0))
    except Exception as e:
        print("Błąd podczas zgłaszania webhooka:", e)
    finally:
        os._exit(0)

def delayed_report():
    import time
    time.sleep(1)  # mała pauza żeby API na pewno było gotowe
    report_to_centrala()

def run_task():
    # Start raportowania w tle po odczekaniu
    threading.Thread(target=delayed_report, daemon=True).start()
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)