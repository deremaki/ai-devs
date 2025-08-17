import os, json, pathlib, time
from typing import Dict, List, Optional
from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from s04e05.utils import (
    load_notes_text, fetch_questions, normalize_answer, send_report,
    parse_incorrect_info, OUT_DIR
)
from s04e05.prompts import SYSTEM_PROMPT, user_prompt_first, user_prompt_retry
from utils.answer_sender import AnswerSender


load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "notes"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

llm = OpenAIClient()

#pytania
#{
#    "01": "Do którego roku przeniósł się Rafał",
#    "02": "Kto wpadł na pomysł, aby Rafał przeniósł się w czasie?",
#    "03": "Gdzie znalazł schronienie Rafał? Nazwij krótko to miejsce",
#    "04": "Którego dnia Rafał ma spotkanie z Andrzejem? (format: YYYY-MM-DD)",
#    "05": "Gdzie się chce dostać Rafał po spotkaniu z Andrzejem?"
#}

#odpowiedzi
# {
#            "01": "2019",
#            "02": "Adam",
#            "03": "Jaskinia",
#            "04": "2024-11-12",
#            "05": "Lubawa"
#        }


MAX_ROUNDS = 6

def answer_one_llm(client: OpenAIClient, notes_text: str, qid: str, question: str,
                   prev_answer: Optional[str] = None, hint: Optional[str] = None) -> str:
    if prev_answer and hint:
        user = user_prompt_retry(notes_text, qid, question, prev_answer, hint)
    else:
        user = user_prompt_first(notes_text, qid, question)

    raw = client.chat(
        user_message=user,
        system_prompt=SYSTEM_PROMPT,
        model = "gpt-4.1-mini"
    )
    return normalize_answer(raw)

def pass_once(client: OpenAIClient, notes_text: str, questions: Dict[str, str],
              prev_per_qid: Dict[str, str] | None = None,
              hints_per_qid: Dict[str, str] | None = None) -> Dict[str, str]:
    answers: Dict[str, str] = {}
    for qid, qtext in questions.items():
        prev = (prev_per_qid or {}).get(qid)
        hint = (hints_per_qid or {}).get(qid)
        ans = answer_one_llm(client, notes_text, qid, qtext, prev_answer=prev, hint=hint)
        answers[qid] = ans
    return answers

def run_task():
    load_dotenv()
    apikey = os.getenv("C3NTRALA_API_KEY")
    if not apikey:
        raise RuntimeError("Brak C3NTRALA_API_KEY w .env")

    notes_text = load_notes_text()
    questions = fetch_questions()

    client = OpenAIClient()

    # Runda 1: odpowiedzi dla wszystkich pytań
    answers = pass_once(client, notes_text, questions)
    OUT_DIR.joinpath("answers-pass1.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")

    # Wyślij i iteruj na podstawie hintów
    round_idx = 1
    history_prev: Dict[str, str] = {}  # ostatnia odesłana odpowiedź per qid
    while round_idx <= MAX_ROUNDS:
        resp = send_report(apikey, answers)
        code = resp.get("code")
        if code == 0:
            print("Sukces — wszystkie odpowiedzi poprawne.")
            print("Flaga: " + resp.get("message"))
            break

        # wyciągnij info o błędzie (zakładamy, że centrala daje 1 błąd na raz)
        qid, hint, prev_sent = parse_incorrect_info(resp)
        if not qid:
            print("Nie udało się zidentyfikować QID z odpowiedzi centrali. Kończę.")
            break

        # ustaw prevSent: jeżeli centrala nie zwróciła, użyj tego, co ostatnio wysłaliśmy
        if not prev_sent:
            prev_sent = answers.get(qid, "")

        # zbuduj 'retry' tylko dla jednego pytania z hintem
        retry_hints = {qid: hint} if hint else {}
        prev_for_qid = {qid: prev_sent} if prev_sent else {}

        # przepisz tylko błędną odpowiedź:
        corrected = pass_once(client, notes_text, {qid: questions[qid]},
                              prev_per_qid=prev_for_qid, hints_per_qid=retry_hints)
        answers[qid] = corrected[qid]

        # zapisz log z rundy
        OUT_DIR.joinpath(f"answers-pass{round_idx+1}.json").write_text(
            json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        round_idx += 1
        time.sleep(0.8)  # delikatny backoff

    # finalny stan (nawet jeśli nie code==0)
    OUT_DIR.joinpath("answers-final.json").write_text(json.dumps(answers, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Zakończono run_task().")
    


def run_solution():
    answers = {
            "01": "2019",
            "02": "Adam",
            "03": "Jaskinia",
            "04": "2024-11-12",
            "05": "Lubawa"
        }
    final_resp = sender.send(answers)
    print("Zgłoszenie zakończone:", final_resp)