import json
import openai
import os
from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

model_name = "ft:gpt-4.1-mini-2025-04-14:personal:ai-devs-s04-e02:BzrHUPxK"
verify_path = "s04e02/lab_data/verify.txt"

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "research"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

llm = OpenAIClient()

def make_finetune_jsonl(correct_path = "s04e02/lab_data/correct.txt", incorrect_path = "s04e02/lab_data/incorrect.txt", output_path = "s04e02/lab_data/finetune_data.jsonl"):
    data = []

    # Dodaj poprawne dane
    with open(correct_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append({
                    "messages": [
                        {"role": "system", "content": "validate data"},
                        {"role": "user", "content": line},
                        {"role": "assistant", "content": "1"}
                    ]
                })

    # Dodaj niepoprawne dane
    with open(incorrect_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                data.append({
                    "messages": [
                        {"role": "system", "content": "validate data"},
                        {"role": "user", "content": line},
                        {"role": "assistant", "content": "0"}
                    ]
                })

    # Zapisz do JSONL
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            

def validate_finetune_values():

    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    valid_ids = []

    with open(verify_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        sample_id = line[:2]
        data = line[3:]  # zakładamy format: "01,dane,dalej"

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "validate data"},
                {"role": "user", "content": data}
            ]
        )

        result = response.choices[0].message.content.strip()

        if result == "1":
            valid_ids.append(sample_id)

    # Finalny format odpowiedzi
    answer = [id_ for id_ in valid_ids]
    print("Answer to report:\n", answer)

    return answer


def run_task():
    #make_finetune_jsonl()

    answer = validate_finetune_values()

    final_resp = sender.send(answer)
    print("Zgłoszenie zakończone:", final_resp)
