import os
import requests
from llm_client.openai_client import OpenAIClient
from s01e03.s01e03 import load_json_from_url, fix_test_data, prepare_submission, save_submission_json

llm = OpenAIClient()

def llm_answer_function(question: str) -> str:
    
    print("LLM question:", question)

    with open("s01e03/system_prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    system_prompt = prompt_template
    user_prompt = "Answer the following question: " + question
    
    answer = llm.chat(
        user_message=user_prompt,
        system_prompt=system_prompt
    )

    print("LLM answer:", answer)
    return answer


def run_s01e03():
    api_key = os.getenv("C3NTRALA_API_KEY")
    data_url = f"https://c3ntrala.ag3nts.org/data/{api_key}/json.txt"
    output_path = "submission.json"

    raw_data = load_json_from_url(data_url)
    fixed_data = fix_test_data(raw_data, llm_answer_function)
    submission = prepare_submission(fixed_data, api_key)
    save_submission_json(submission, output_path)
    print(f"✅ Submission saved to {output_path}")

        # Send submission to endpoint
    print("📡 Sending submission to server...")
    response = requests.post("https://c3ntrala.ag3nts.org/report", json=submission)
    response.raise_for_status()
    print("🎉 Response from server:")
    print(response.text)