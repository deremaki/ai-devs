import json
import os
import string
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"



def query_places( query: str) -> list[str]:
    

    url = f"https://c3ntrala.ag3nts.org/places"
    payload = {
        "apikey": API_KEY,
        "query": query.upper()
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    people = data["message"].split()

    return people