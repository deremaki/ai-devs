# s00e00/s00e00.py

import requests
from key import API_KEY

def run_s00e00():
    # Step 1: Get the data
    data_url = "https://poligon.aidevs.pl/dane.txt"
    response = requests.get(data_url)
    response.raise_for_status()
    strings = response.text.strip().split()

    # Step 2: Prepare the answer
    payload = {
        "task": "POLIGON",
        "apikey": API_KEY,
        "answer": strings
    }

    # Step 3: Send it to the verify endpoint
    verify_url = "https://poligon.aidevs.pl/verify"
    result = requests.post(verify_url, json=payload)
    print(result.json())