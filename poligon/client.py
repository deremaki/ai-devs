# poligon/client.py

import requests
from key import API_KEY

class PoligonClient:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://poligon.aidevs.pl"

    def upload_solution(self, task: str, answer):
        payload = {
            "task": task,
            "apikey": self.api_key,
            "answer": answer
        }

        url = f"{self.base_url}/verify"
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"code": -1, "message": str(e)}