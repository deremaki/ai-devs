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

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "gps"
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)

llm = OpenAIClient()


logging.basicConfig(level=logging.DEBUG, format="[%(levelname)s] %(message)s")
log = logging.getLogger("agent-s05e02")


class Tools:

    def get_user_id_by_name(self, name: str):
        log.debug(f"[TOOL] get_user_id_by_name(name={name!r})")
        return query_userID(name)


    def get_location_by_user_id(self, user_id: str):
        log.debug(f"[TOOL] get_location_by_user_id(user_id={user_id!r})")
        return query_gps(user_id)


    def get_users_in_city(self, city: str) -> List[str]:
        log.debug(f"[TOOL] get_users_in_city(city={city!r})")
        return query_places(city)


def run_task():

    starting_query = "Wiemy, że Rafał planował udać się do Lubawy, ale musimy się dowiedzieć, kto tam na niego czekał. Nie wiemy, czy te osoby nadal tam są. Jeśli to możliwe, to spróbuj namierzyć ich za pomocą systemu GPS. Jest szansa, że samochody i elektronika, z którą podróżują, zdradzą ich pozycję. A! Ważna sprawa. Nie próbuj nawet wyciągać lokalizacji dla Barbary, bo roboty teraz monitorują każde zapytanie do API i gdy zobaczą coś, co zawiera jej imię, to podniosą alarm. Zwróć nam więc koordynaty wszystkich osób, ale koniecznie bez Barbary."

    # ====== STEP 1: general planning


    # ====== STEP 2: main loop -> exit on ready to final answer


    # ====== STEP 3: prepare and give final answer

