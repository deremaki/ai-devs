from llm_client.openai_client import OpenAIClient
import requests
import re

LOGIN_URL = "https://xyz.ag3nts.org/"
USERNAME = "tester"
PASSWORD = "574e112a"

llm = OpenAIClient()

def get_question():
    response = requests.get(LOGIN_URL)
    if response.status_code != 200:
        raise Exception("Failed to fetch login page.")

    # Look for <p id="human-question">QUESTION TEXT</p>
    match = re.search(r'<p id="human-question">(.*?)</p>', response.text, re.DOTALL)
    if not match:
        raise Exception("Could not find question with id='human-question'.")
    
    raw_question = match.group(1).strip()

    # Clean "Question:" prefix and <br /> tag
    cleaned = raw_question.replace("Question:", "").replace("<br />", "").strip()
    print("🔍 Extracted question:", cleaned)
    return cleaned

def get_answer(question):
    print("Sending question to LLM...")

    with open("s01e01/prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    system_prompt = prompt_template
    user_prompt = "Odpowiedz na to pytanie: " + question
    
    # Use LLM
    answer = llm.chat(
        user_message=user_prompt,
        system_prompt=system_prompt
    )
    
    print("LLM answer:", answer)
    return answer.strip()

def submit_login(username, password, answer):
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"username": username, "password": password, "answer": answer}
    response = requests.post(LOGIN_URL, headers=headers, data=data)
    return response.text

def follow_secret_url(response_text):
    # Look for the flag in {{FLG:...}} format
    flag_match = re.search(r'\{\{FLG:[^}]+\}\}', response_text)
    if not flag_match:
        raise Exception("Flag not found on the secret page.")

    flag = flag_match.group(0)

    return flag

def run_task():
    question = get_question()
    answer = get_answer(question)
    login_response = submit_login(USERNAME, PASSWORD, answer)
    secret_content = follow_secret_url(login_response)
    print("\n🎉 FLAG FOUND 🎉\n", secret_content)