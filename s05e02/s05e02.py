import os, json, requests, re, logging

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

from s05e02.database import query_userID
from s05e02.gps import query_gps
from s05e02.places import query_places

from s05e02.prompts import DECIDE_PROMPT,DECIDE_SYSTEM,REFLECTION_PROMPT, REFLECTION_SYSTEM, VERIFY_PROMPT,VERIFY_SYSTEM

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "gps"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

MAX_STEPS = 25

llm = OpenAIClient()


class Tools:

    def get_user_id_by_name(self, name: str):
        print(f"[TOOL] get_user_id_by_name(name={name!r})")
        return query_userID(name)


    def get_location_by_user_id(self, user_id: str):
        print(f"[TOOL] get_location_by_user_id(user_id={user_id!r})")
        return query_gps(user_id)


    def get_users_in_city(self, city: str) -> List[str]:
        print(f"[TOOL] get_users_in_city(city={city!r})")
        return query_places(city)
    
@dataclass
class AgentState:
# Cele wyekstrahowane w refleksji
    target_people: List[str] = field(default_factory=list)
    target_cities: List[str] = field(default_factory=list)


    # Wiedza z narzędzi
    user_ids: Dict[str, str] = field(default_factory=dict) # name -> user_id
    locations: Dict[str, Tuple[str, str]] = field(default_factory=dict) # name -> {lat, lon}
    city_users: Dict[str, List[str]] = field(default_factory=dict) # city -> [names]


    # Historia (narzędzia, decyzje)
    history: List[Dict[str, Any]] = field(default_factory=list)


    def snapshot(self) -> Dict[str, Any]:
        return {
            "target_people": self.target_people,
            "target_cities": self.target_cities,
            "user_ids": self.user_ids,
            "locations": self.locations,
            "city_users": self.city_users,
    }

def _extract_json(s: str) -> str:
    """Wyciąga pierwszy blok JSON ze stringa (toleruje bałagan)."""
    m = re.search(r"\{[\s\S]*\}$", s.strip())
    if m:
        return m.group(0)
    m = re.search(r"\{[\s\S]*\}", s)
    return m.group(0) if m else s


def _json_loads_safe(s: str) -> Any:
    try:
        return json.loads(_extract_json(s))
    except Exception as e:
        print(f"Błąd parsowania JSON: {e}. Tekst=\n{s}")
        raise

def run_task():

    starting_query = "Wiemy, że Rafał planował udać się do Lubawy, ale musimy się dowiedzieć, kto tam na niego czekał. Nie wiemy, czy te osoby nadal tam są. Jeśli to możliwe, to spróbuj namierzyć ich za pomocą systemu GPS. Jest szansa, że samochody i elektronika, z którą podróżują, zdradzą ich pozycję. A! Ważna sprawa. Nie próbuj nawet wyciągać lokalizacji dla Barbary, bo roboty teraz monitorują każde zapytanie do API i gdy zobaczą coś, co zawiera jej imię, to podniosą alarm. Zwróć nam więc koordynaty wszystkich osób, ale koniecznie bez Barbary."
    tools = Tools()
    run_agent(starting_query, tools)

def run_agent(starting_query, tools):

    # ====== STEP 1: general planning / reflection
    raw_response = llm.chat(
        user_message=REFLECTION_PROMPT.format(task=starting_query),
        system_prompt=REFLECTION_SYSTEM,
        model="gpt-4.1-mini"
    )
    try:
        reflection = json.loads(raw_response)
    except Exception as e:
        print("[ERROR] Nie udało się sparsować JSON:", e)
        print(raw_response)
        raise

    state = AgentState()
    state.target_cities = reflection.get("miejsca")
    state.history.append({"step": "reflection", "data": reflection})

    print("[REFLEKSJA] Ogólne rozumowanie:", reflection.get("notatki"))
    print("[REFLEKSJA] Miasta:", state.target_cities)
    print("[STATE SNAPSHOT]", state.snapshot())

    # ====== STEP 2: main loop -> exit on ready to final answer
    for step in range(1, MAX_STEPS):
        decide_user_msg = (
            DECIDE_PROMPT
            .replace("{reflection}", json.dumps(reflection, ensure_ascii=False))
            .replace("{state}", json.dumps(state.snapshot(), ensure_ascii=False))
            .replace("{short_history}", json.dumps(state.history, ensure_ascii=False))
        )
        decision_raw = llm.chat(
            user_message=decide_user_msg,
            system_prompt=DECIDE_SYSTEM,
            model="gpt-4.1-mini"
        )
        print(f"\n [STEP {step}] Początek stepu \n")

        print("[DECISION RAW]", decision_raw)
        decision = json.loads(decision_raw)
        state.history.append({"step": "decide", "data": decision})

        if decision.get("ready") is True:
            print(f"[STEP {step}] Gotowe -> wychodzę z pętli")
            break

        action = (decision.get("action") or {})
        tool = action.get("tool")
        args = action.get("args", {})
        print(f"[STEP {step}] Wywołuję narzędzie: {tool}({args})")

        if tool == "GET_USER_ID":
            name = args.get("name")
            uid = tools.get_user_id_by_name(name)
            state.user_ids[name] = uid
            result = {"user_id": uid}

        elif tool == "GET_GPS_LOCATION":
            user_id = args.get("user_id")
            name = args.get("name")
            if not user_id and name:
                user_id = state.user_ids.get(name)
            lat, lon = tools.get_location_by_user_id(user_id)
            if lat and lon and name:
                state.locations[name] = (lat, lon)
            result = (lat, lon)

        elif tool == "LIST_USERS_IN_CITY":
            city = args.get("city")
            users = tools.get_users_in_city(city)
            state.target_people.append(users)
            state.city_users[city] = users
            result = users

        else:
            result = {"error": f"Nieznane narzędzie {tool}"}

        print(f"[STEP {step}] Wynik narzędzia:", result)
        state.history.append({"step": "tool", "tool": tool, "args": args, "result": result})

        print("[STATE SNAPSHOT]", state.snapshot())

    # Po pętli — podgląd stanu
    print("[FINAL STATE SNAPSHOT]", state.snapshot())

    # ====== STEP 3: prepare and give final answer
    final_answer = {}
    for name, coords in state.locations.items():
        final_answer[name] = {
            "lat": coords[0],
            "lon": coords[1]
        }

    print("[FINAL ANSWER]", json.dumps(final_answer, ensure_ascii=False, indent=2))

    print("[ANSWER] Sending answers to Centrala…")
    resp = sender.send(final_answer)  