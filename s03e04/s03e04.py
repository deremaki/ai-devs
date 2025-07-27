import json
import os
import requests
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

load_dotenv()

TASK_NAME = "loop"
API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"

llm = OpenAIClient()
sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)


def print_entities(people: set[str], places: set[str]):
    print("🧍‍♂️ Osoby do sprawdzenia:")
    for person in people:
        print(f"  - {person}")

    print("📍 Miejsca do sprawdzenia:")
    for place in places:
        print(f"  - {place}")

def query_centrala(endpoint: str, query: str) -> list[str]:
    assert endpoint in ("people", "places"), "Endpoint musi być 'people' albo 'places'"
    

    url = f"https://c3ntrala.ag3nts.org/{endpoint}"
    payload = {
        "apikey": API_KEY,
        "query": query
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()
    
    data = response.text
    return data


def extract_entities_from_text_llm(note: str):
    system_prompt = (
        "Otrzymasz treść notatki z imionami osób lub nazwami miast. Twoim zadaniem jest wyodrębnić dwie listy:\n"
        "- lista imion osób (ZAWSZE w mianowniku, BEZ polskich znaków)\n"
        "- lista miast (ZAWSZE w mianowniku, BEZ polskich znaków)\n"
        "- AZAZEL to imie\n"
        "- ABSOLUTNIE NIE ZMYSLAJ NAZW\n"
        "Zwróć wynik jako poprawny JSON w formacie:\n"
        "{ \"people\": [\"IMIE1\", \"IMIE2\", ...], \"places\": [\"MIASTO1\", \"MIASTO2\", ...] }"
    )

    print("ANALIZOWANA NOTATKA: " + note)

    response = llm.chat(
        user_message=note,
        system_prompt=system_prompt
    )

    data = json.loads(response.replace("```json", "").replace("```", "").strip())
    people = [p.upper() for p in data.get("people", [])]
    places = [p.upper() for p in data.get("places", [])]

    print("------- Wyczytane NOWE entities: -------")
    print_entities(people, places)

    return people, places

def extract_entities_from_text(note: str, query: str):

    print("ANALIZOWANA NOTATKA: " + note)

    if query == "place":
        people = set(note.split())
        places = {}

    if query == "person":
        places = set(note.split())
        people = {}
    #print("------- Wyczytane NOWE entities: -------")
    #print_entities(people, places)

    return people, places

def initial_people_and_places():
    people = {"BARBARA", "ALEKSANDER", "ANDRZEJ", "RAFAL"}
    places = {"KRAKOW", "WARSZAWA"}

    print("------- Wyczytane NOWE entities: -------")
    print_entities(people, places)

    return people, places
    

def analyze_for_barbara_presence(answer_text: str, query_city: str) -> str | None:
    """
    Pyta LLM-a, czy odpowiedź zawiera informację o aktualnym pobycie Barbary.
    Jeśli tak – LLM ma zwrócić dokładną nazwę miasta (dokładnie taką, jak pojawiła się w odpowiedzi z API).
    """
    print(f"[INFO] Sprawdzam czy Barbara przebywa w {query_city}. Notatka: {answer_text}")
    prompt = (
        f"Czy z tej notatki wynika gdzie AKTUALNIE przebywa BARBARA?\n"
        f"Jeśli tak, zwróć tylko nazwę miasta dokładnie tak, co do znaku, jak występuje w tekście.\n"
        f"Jeśli nie, zwróć NIE."
    )

    response = llm.chat(user_message=answer_text, system_prompt=prompt)
    print("[INFO] Odpowiedź z LLMa: " + response)
    cleaned = response.strip().upper()
    if cleaned == "NIE":
        return None
    return cleaned

def run_task():

    #init sets
    print("[INFO] Inicjalizacja pustych setów")
    people: set[str] = set()
    places: set[str] = set()

    #seed sets from barbara.txt
    print("[INFO] Początek pracy - parsuję notatkę barbara.txt.")

    with open("s03e04/barbara.txt", "r", encoding="utf-8") as f:
        note = f.read()
    #new_people, new_places = extract_entities_from_text(note)
    new_people, new_places = initial_people_and_places()
    people.update(new_people)
    places.update(new_places)

    #lecimy dalej

    already_processed = []
    koniec = False

    while people or places and not koniec:
        print("[INFO] ======================= Przetwarzanie....  ======================= ")
        print_entities(people, places)
        searching_for_people = False
        searching_for_place = False

        if people:
            searching_for_people = True
            person = people.pop()

            print(f"\n[INFO] 🔍 Sprawdzam osobę: {person}")

            if person in already_processed:
                print(f"[INFO] Sprawdzalismy juz: {person}, skip...")
                continue
            else:
                already_processed.append(person)

            try:
                results = query_centrala("people", person)
            except Exception as e:
                print(f"❌ SKIP, odpowiedź dla: {person}: " + str(e))
                continue
        
        else:
            searching_for_place = True
            place = places.pop()
            print(f"\n[INFO] 📍 Sprawdzam miejsce: {place}")

            if place in already_processed:
                print(f"[INFO] Sprawdzalismy juz: {place}, skip...")
                continue
            else:
                already_processed.append(place)

            try:
                results = query_centrala("places", place)
            except Exception as e:
                print(f"❌ SKIP, odpowiedź dla: {place}: " + str(e))
                continue

        result_text = json.loads(results)["message"]
        if "RESTRICTED" in result_text:
            print("Odpowiedź: " + result_text)
            print("[INFO] SKIP")
            continue

        print("[INFO] Analizuję notatkę...")
        new_people, new_places = extract_entities_from_text(result_text, "person" if searching_for_people else "place")
        people.update(new_people)
        places.update(new_places)

        # sprawdzamy, czy odpowiedź zawiera info o Barbarze
        
        if searching_for_place:
            print("[INFO] Sprawdzamy czy wspomniane miasto zawiera informacje o Barbarze...")
            if "BARBARA" in new_people:
                barbara_city = place
                
                print(f"🎯 Podejrzewamy, że Barbara jest w: {barbara_city}")
                response = sender.send(barbara_city)
                try:
                    data = response.json()
                    if data.get("code") == 0:
                        print("✅ Trafiona odpowiedź!")
                        answer = barbara_city
                        koniec = True
                        break
                        #idz do konca zeby zlapac secret flage
                        #continue
                    elif data.get("code") == -1000:
                        print(f"🛑 Barbara nie jest w {barbara_city}, szukamy dalej.")
                    else:
                        print("⚠️ Niespodziewana odpowiedź:", data)
                except Exception as e:
                    print("❌ Błąd przy analizie odpowiedzi z /report")
                    raise e



    print("[INFO] Task completed successfully.")
    

def run_secret():
    print(query_centrala("places", "RADOM"))