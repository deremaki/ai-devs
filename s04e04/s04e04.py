# s04e04/s04e04.py
import os
import json
import re
import threading
import requests
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, ConfigDict, constr
import uvicorn
from llm_client.openai_client import OpenAIClient
from s04e04.map import MAP

llm = OpenAIClient()

app = FastAPI(title="AIDevs s04e04 webhook", version="1.0.0")


class DroneRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")  # odrzuć nieznane pola
    instruction: constr(strip_whitespace=True, min_length=1)

@app.post("/webhook")
async def webhook(req: Request, body: DroneRequest):
    # Wymuś Content-Type: application/json
    ct = req.headers.get("content-type", "")
    if "application/json" not in ct:
        raise HTTPException(status_code=415, detail="Content-Type must be application/json")
    
    print("Received instruction: ", body.instruction)

    coords_instructions = handle_instruction(body.instruction)
    print("Interpreted coordinates: ", coords_instructions)
    coords = get_map_value(coords_instructions)

    print("Coords: ", coords)


    return {
        "description": coords,
        "received": {"instruction": body.instruction},
        "interpreted_coordinates": coords_instructions
    }

def handle_instruction(instruction: str):
    with open("s04e04/prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    system_prompt = prompt_template
    user_prompt = "Przygotuj współrzędne dla danego opisu: " + instruction
    
    answer = llm.chat(
        user_message=user_prompt,
        system_prompt=system_prompt
    )

    return answer


def get_map_value(json_str: str) -> str:
    try:
        data = json.loads(json_str)
        x = int(data["x"])
        y = int(data["y"])
        return MAP[y][x]  # y = wiersz, x = kolumna
    except (KeyError, ValueError, IndexError, TypeError):
        return "błąd mapy"

def report_to_centrala():
    api_key = os.getenv("C3NTRALA_API_KEY")
    public_url = os.getenv("PUBLIC_WEBHOOK_URL")  # np. z ngrok
    if not api_key or not public_url:
        print("Brak C3NTRALA_API_KEY lub PUBLIC_WEBHOOK_URL w env.")
        return
    
    payload = {
        "task": "webhook",
        "apikey": api_key,
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
    time.sleep(2)  # mała pauza żeby API na pewno było gotowe
    report_to_centrala()

def run_task():
    # Start raportowania w tle po odczekaniu
    threading.Thread(target=delayed_report, daemon=True).start()
    
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)