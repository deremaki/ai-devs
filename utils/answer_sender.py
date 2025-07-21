import os
import requests
import json

class AnswerSender:
    def __init__(self, task_name: str, api_key: str | None = None):
        self.task_name = task_name
        self.api_key = api_key or os.getenv("C3NTRALA_API_KEY")
        if not self.api_key:
            raise ValueError("Brakuje API KEY – ustaw zmienną C3NTRALA_API_KEY")

    def send(self, answer: str):
        url =  "https://c3ntrala.ag3nts.org/report"
        payload = {
            "task": self.task_name,
            "apikey": self.api_key,
            "answer": answer
        }
        print("Treść odpowiedzi:")
        
        print(json.dumps(payload, indent=2, ensure_ascii=False))


        response = requests.post(url, json=payload)
        print(f"✅ Odpowiedź z serwera: {response.text}")
        return response