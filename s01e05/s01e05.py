import os
import requests
import re
from llm_client.openai_client import OpenAIClient

llm = OpenAIClient()

def run_task():
    api_key = os.getenv("C3NTRALA_API_KEY")
    url = f"https://c3ntrala.ag3nts.org/data/{api_key}/cenzura.txt"
    response = requests.get(url)
    response.encoding = "utf-8"
    text = response.text

    print("Nieocenzurowany tekst:", text)

    censored = censor_text(text)

    payload = {
        "task": "CENZURA",
        "apikey": api_key,
        "answer": censored
    }

    print("Ocenzurowany tekst:", censored)

    report_url = "https://c3ntrala.ag3nts.org/report"
    report_response = requests.post(report_url, json=payload)
    print("Status:", report_response.status_code)
    print("Response:", report_response.text)

def censor_text(text):
    # Cenzura imienia i nazwiska (np. "Jan Nowak")
    with open("s01e05/prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    system_prompt = prompt_template
    user_prompt = "Cenzor the following text: " + text
    
    answer = llm.chat(
        user_message=user_prompt,
        system_prompt=system_prompt
    )

    return answer