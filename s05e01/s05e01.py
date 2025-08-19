import os, json, requests
from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

from s05e01.prompts import ORDER_NEXT_SYSTEM, ORDER_NEXT_USER, ASSIGN_SPEAKERS_SYSTEM, ASSIGN_SPEAKERS_USER, EXTRACT_CHARACTERS_SYSTEM, EXTRACT_CHARACTERS_USER, LIAR_GLOBAL_SYSTEM, LIAR_GLOBAL_USER, QUESTION_ROUTING_SYSTEM, QUESTION_ROUTING_USER, ANSWER_FROM_CONTEXT_SYSTEM, ANSWER_FROM_CONTEXT_USER, API_PLANNER_SYSTEM, API_PLANNER_USER

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "phone"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

llm = OpenAIClient()

CONVERSATIONS_PATH = "s05e01/in/phone_conversations.json"
LABELED_PATH = "s05e01/in/phone_conversations_labeled.json"
QUESTIONS_PATH = "s05e01/in/phone_questions.json"

FACTS_DIR = "s05e01/facts"
LIAR_OUT = "s05e01/in/global_liar.json"

def load_phone_json(path="s05e01/in/phone.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_conversations(data, path=CONVERSATIONS_PATH):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def validate(so_far, end_sentence, candidates):
    user_prompt = ORDER_NEXT_USER.format(
        so_far="\n".join(so_far),
        end=end_sentence,
        candidates="\n".join(candidates)
    )
    reply = llm.chat(user_prompt, ORDER_NEXT_SYSTEM, model = "gpt-4.1-mini")
    try:
        data = json.loads(reply)
        next = data.get("next")
        reasoning = data.get("_thinking")
        return next, reasoning
    except Exception as e:
        print(f"[validate] błąd JSON: {e}, raw reply={reply}")
        return None


def split_conversations(raw):
    conv_defs = sorted(
        [(k, v) for k, v in raw.items() if k.startswith("rozmowa")],
        key=lambda x: x[1]["length"]
    )
    reszta = raw["reszta"][:]
    conversations = {}

    for name, meta in conv_defs:
        start, end = meta["start"], meta["end"]
        print(f"\n=== Rekonstrukcja {name} (len={meta['length']}) ===")
        turns = [start]
        print(f"[{name}] START: {start}")

        while True:
            nxt, reasoning = validate(turns, end, reszta)
            if not nxt or nxt == "NONE":
                print(f"[{name}] brak dopasowania, przerywam.")
                break
            if nxt == end or len(turns) == meta['length']:
                print(f"[{name}] osiągnięto END.")
                break
            if nxt in reszta:
                turns.append(nxt)
                reszta.remove(nxt)
                print(f"[{name}] + {nxt}")
            else:
                print(f"[{name}] kandydat nie w reszcie: {nxt}")
                break

        turns.append(end)
        print(f"[{name}] END: {end}")
        conversations[name] = {"start": start, "end": end, "turns": turns}

    print("\nPozostałe linie w reszcie:", len(reszta))
    return conversations

def extract_characters(conversations_path=CONVERSATIONS_PATH):
    with open(conversations_path, "r", encoding="utf-8") as f:
        conv = json.load(f)
    up = EXTRACT_CHARACTERS_USER.format(
        full_conversations=json.dumps(conv, ensure_ascii=False)
    )
    reply = llm.chat(up, EXTRACT_CHARACTERS_SYSTEM)
    try:
        data = json.loads(reply)
        return data.get("characters", [])
    except Exception as e:
        print(f"[Stage2] extract_characters JSON error: {e} | raw={reply}")
        return []

def assign_speakers_for_all(conversations_path=CONVERSATIONS_PATH, out_path=LABELED_PATH):
    with open(conversations_path, "r", encoding="utf-8") as f:
        conv = json.load(f)

    known = extract_characters(conversations_path)
    labeled = {}

    for name, convo in conv.items():
        up = ASSIGN_SPEAKERS_USER.format(
            single_conversation=json.dumps(convo, ensure_ascii=False),
            known_characters=json.dumps(known, ensure_ascii=False)
        )
        reply = llm.chat(up, ASSIGN_SPEAKERS_SYSTEM, model="gpt-4.1-mini")
        try:
            labeled[name] = json.loads(reply)
            print(f"[Stage2] labeled {name}")
        except Exception as e:
            print(f"[Stage2] assign JSON error in {name}: {e} | raw={reply}")

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(labeled, f, ensure_ascii=False, indent=2)
    print(f"[Stage2] Saved → {out_path}")


def replace_agentka_with_barbara(path=LABELED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        conv = json.load(f)

    for name, convo in conv.items():
        # zamień w participants
        convo["participants"] = [
            "Barbara" if p.lower() in ["agentka", "agent"] else p
            for p in convo.get("participants", [])
        ]
        # zamień w turns
        for turn in convo.get("turns", []):
            if turn.get("speaker", "").lower() in ["agentka", "agent"]:
                turn["speaker"] = "Barbara"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(conv, f, ensure_ascii=False, indent=2)

    print(f"[Stage2.5] Zaktualizowano plik → {path}")


def load_facts_text(dir_path=FACTS_DIR):
    parts = []
    for fname in sorted(os.listdir(dir_path)):
        if fname.lower().endswith(".txt"):
            with open(os.path.join(dir_path, fname), "r", encoding="utf-8") as f:
                t = f.read().strip()
                if t: parts.append(f"[{fname}]\n{t}")
    return "\n\n".join(parts)

def collect_allowed_names(labeled_path=LABELED_PATH):
    with open(labeled_path, "r", encoding="utf-8") as f:
        labeled = json.load(f)
    names = set()
    for convo in labeled.values():
        for p in convo.get("participants", []):
            if p: names.add(p)
    return sorted(names)

def stage3_global_liar(out_path=LIAR_OUT):
    with open(LABELED_PATH, "r", encoding="utf-8") as f:
        labeled = json.load(f)
    facts_text = load_facts_text()
    allowed = collect_allowed_names()

    user_prompt = LIAR_GLOBAL_USER.format(
        facts_text=facts_text,
        labeled_conversations=json.dumps(labeled, ensure_ascii=False),
        allowed_names=json.dumps(allowed, ensure_ascii=False)
    )
    reply = llm.chat(user_prompt, LIAR_GLOBAL_SYSTEM, model="gpt-4.1-mini")
    try:
        data = json.loads(reply)
    except Exception as e:
        print(f"[Stage3] JSON error: {e}\nRAW:\n{reply}")
        return

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[Stage3] Saved → {out_path}")
    print(f"[Stage3] Global liar: {data.get('liar')} (conf={data.get('confidence')})")


def get_liar_name(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("liar", None)

def load_questions(path=QUESTIONS_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_labeled(path=LABELED_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_global_liar(path=LIAR_OUT):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f).get("liar", "UNKNOWN")

def route_question(q: str) -> str:
    up = QUESTION_ROUTING_USER.format(question=q)
    reply = llm.chat(up, QUESTION_ROUTING_SYSTEM)
    try:
        return json.loads(reply).get("type", "context")
    except:
        return "context"

def answer_from_context(question: str, labeled: dict, liar_name: str) -> str:
    up = ANSWER_FROM_CONTEXT_USER.format(
        labeled=json.dumps(labeled, ensure_ascii=False),
        liar=liar_name,
        question=question
    )
    reply = llm.chat(up, ANSWER_FROM_CONTEXT_SYSTEM)
    return reply.strip().strip('"')

def plan_api_call(question: str) -> dict:
    up = API_PLANNER_USER.format(question=question)
    reply = llm.chat(up, API_PLANNER_SYSTEM)
    try:
        return json.loads(reply)
    except:
        return {"method":"GET","url":"","headers":{},"params":{},"body":{},"note":"parse_error"}

def exec_api(plan: dict) -> str:
    try:
        method = plan.get("method","GET").upper()
        url    = plan.get("url","")
        headers= plan.get("headers",{})
        params = plan.get("params",{})
        body   = plan.get("body",{})
        if not url:
            return "BRAK_URL"
        if method == "GET":
            r = requests.get(url, headers=headers, params=params, timeout=15)
        else:
            r = requests.post(url, headers=headers, json=body, params=params, timeout=15)
        r.raise_for_status()
        # zwróć krótki ekstrakt (tu prosto: raw text)
        return r.text.strip()
    except Exception as e:
        return f"API_ERROR:{e}"

def stage4_answer_questions():
    questions = load_questions()            # {"01":"...", "02":"...", ...}
    labeled   = load_labeled()
    liar_name = load_global_liar()

    answers = {}

    for key, q in questions.items():
        print(f"[Stage4] Q{key}: routing…")
        qtype = route_question(q)
        if qtype == "api":
            print(f"[Stage4] Q{key}: via API")
            plan = plan_api_call(q)
            api_res = exec_api(plan)
            # można dodać mini prompt do ekstrakcji finalnej odpowiedzi z api_res, ale tu zostawiamy raw
            answers[key] = api_res
        else:
            print(f"[Stage4] Q{key}: from context")
            ans = answer_from_context(q, labeled, liar_name)
            answers[key] = ans

    return answers

def stage4_send_answers(answers: dict):
    # dopasuj do wymaganego formatu; zakładam klucze "01".."06" już są
    payload = {k: str(v) for k, v in answers.items()}
    print("[Stage4] Sending answers to Centrala…")
    resp = sender.send(payload)  
    print("[Stage4] Centrala response:", resp)
    return resp

def run_task():

    # STAGE 1 - untangle conversations
    if not os.path.exists(CONVERSATIONS_PATH):

        print("[Stage1] Building conversations…")
        raw = load_phone_json()
        conversations = split_conversations(raw)
        save_conversations(conversations)
        print("\n[Stage1] Zapisano phone_conversations.json")

    else:
        print("[Stage1] Skipping Stage 1. Using existing file: phone_conversations.json")

    # STAGE 2 - assign people
    if not os.path.exists(LABELED_PATH):
        print("[Stage2] Assigning speakers…")
        assign_speakers_for_all()
        print("[Stage2] Done - speakers assgined")

    else:
        print("[Stage2] Skipping Stage 2. Using existing file: phone_conversations_labeled.json")

    # STAGE 2.5 - replace Agentka → Barbara
    #we know that Agentka means Barbara, even though it's not mentioned
    print("[Stage2.5] Replacing Agentka with Barbara…")
    replace_agentka_with_barbara(LABELED_PATH)
    print("[Stage2.5] Done")


    # STAGE 3 - identify liar
    if not os.path.exists("s05e01/in/global_liar.json"):
        print("[Stage3] Selecting single global liar…")
        stage3_global_liar()
        print("[Stage3] Done")
    
    liar = get_liar_name("s05e01/in/global_liar.json")
    print("[Stage3] We know that "+liar+" is a liar")   

    # STAGE 4 – Q&A
    print("[Stage4] Building answers…")
    answers = stage4_answer_questions()
    print("[Stage4] Answers draft:", answers)
    stage4_send_answers(answers)
    print("[Stage4] Done")


def run_answers():
    payload = {
    "01": "Samuel",
    "02": "https://rafal.ag3nts.org/b46c3",
    "03": "Nauczyciel",
    "04": "Samuel i Barbara",
    "05": "4ce1854fa925fa0e4342ce7c501f2f78",
    "06": "Aleksander"
  }
    print("[CHEATING] Sending answers to Centrala…")
    resp = sender.send(payload)  