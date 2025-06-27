# s00e00/s00e00.py

import requests
from poligon.client import PoligonClient

def run_s00e00():
    # Step 1: Fetch strings from external source
    url = "https://poligon.aidevs.pl/dane.txt"
    response = requests.get(url)
    response.raise_for_status()

    strings = response.text.strip().split()

    # Step 2: Upload answer using reusable client
    client = PoligonClient()
    result = client.upload_solution("POLIGON", strings)

    print(result)