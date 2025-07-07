import json
import re
from typing import Any
import requests


def evaluate_expression(expr: str) -> int | None:
    """Evaluate simple addition expression like '45 + 86'."""
    match = re.match(r"(\d+)\s*\+\s*(\d+)", expr)
    if not match:
        return None
    left = int(match.group(1))
    right = int(match.group(2))
    return left + right


def fix_test_data(data: dict, llm_answer_function) -> dict:
    """Fix all test data entries."""
    fixed_data = []
    for entry in data.get("test-data", []):
        question = entry.get("question")
        correct_answer = evaluate_expression(question)
        if correct_answer is not None:
            entry["answer"] = correct_answer

        # Fill in missing open question answers using LLM if needed
        if "test" in entry:
            q = entry["test"].get("q")
            a = entry["test"].get("a")
            if a is None or a.strip("? ") == "":
                entry["test"]["a"] = llm_answer_function(q)

        fixed_data.append(entry)

    data["test-data"] = fixed_data
    return data


def prepare_submission(data: dict, apikey: str) -> dict:
    data["apikey"] = apikey  # upewniamy się, że wewnętrzny klucz też jest poprawny
    return {
        "task": "JSON",
        "apikey": apikey,
        "answer": data
    }


def load_json_from_url(url: str) -> Any:
    resp = requests.get(url)
    resp.raise_for_status()
    return json.loads(resp.text)


def save_submission_json(submission: dict, path: str):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(submission, f, indent=2, ensure_ascii=False)
