import json
import os
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"



def query_gps( userID: str) -> list[str]:
    

    url = f"https://c3ntrala.ag3nts.org/gps"
    payload = {
        "apikey": API_KEY,
        "userID": userID
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    lat = data["message"]["lat"]
    lon = data["message"]["lon"]
    return lat, lon