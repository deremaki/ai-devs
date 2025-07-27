import os
import requests
from dotenv import load_dotenv
from neo4j import GraphDatabase
from utils.answer_sender import AnswerSender
from llm_client.openai_client import OpenAIClient

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"
TASK_NAME = "connections"


def query_api(sql_query):
    print(f"[QUERY] Executing SQL: {sql_query}")
    response = requests.post(API_URL, json={
        "task": "database",
        "apikey": API_KEY,
        "query": sql_query
    })
    response.raise_for_status()
    json_data = response.json()
    #print(f"[RESPONSE] Received: {json_data}")
    return json_data

def clear_graph(tx):
    tx.run("MATCH (n) DETACH DELETE n")

def create_users(tx, users):
    for user_id, name in users.items():
        tx.run(
            "CREATE (:Person {userId: $userId, name: $name})",
            userId=user_id,
            name=name
        )

def create_connections(tx, edges):
    for user1, user2 in edges:
        tx.run(
            """
            MATCH (a:Person {userId: $u1}), (b:Person {userId: $u2})
            CREATE (a)-[:KNOWS]->(b)
            """,
            u1=user1,
            u2=user2
        )

def find_shortest_path(tx):
    result = tx.run(
        """
        MATCH (start:Person {name: "Rafał"}), (end:Person {name: "Barbara"})
        MATCH path = shortestPath((start)-[:KNOWS*]-(end))
        RETURN [n IN nodes(path) | n.name] AS names
        """
    )
    record = result.single()
    if record:
        return record["names"]
    return None


def run_task():

    #====================GET DATA========================

    result = query_api(f"SHOW CREATE TABLE users;")
    schema = result['reply'][0]['Create Table']
    print(schema)
    result = query_api(f"SHOW CREATE TABLE connections;")
    schema = result['reply'][0]['Create Table']
    print(schema)

    print("Pobieram dane z tabeli 'users'...")
    users_data = query_api("SELECT id, username FROM users;")
    print("📄 SAMPLE USERS:")
    # Parsowanie do dict: {id: username}
    user_id_to_name = {int(user['id']): user['username'] for user in users_data['reply']}

    # Wyświetl przykładowo pierwsze 10
    for uid, name in list(user_id_to_name.items())[:10]:
        print(f"{uid}: {name}")

    print("\nPobieram dane z tabeli 'connections'...")
    connections_data = query_api("SELECT user1_id, user2_id FROM connections;")
    print("🔗 SAMPLE CONNECTIONS:")
    # Parsowanie do listy połączeń jako tuple (int, int)
    connections = [(int(row['user1_id']), int(row['user2_id'])) for row in connections_data['reply']]

    # Przykładowy podgląd
    for edge in connections[:10]:
        print(edge)

    #====================PREP neo4j========================

    # Połączenie z Neo4j
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

    with driver.session() as session:
        print("🧨 Czyszczę grafik...")
        session.write_transaction(clear_graph)

        print("👥 Tworzę węzły użytkowników...")
        session.write_transaction(create_users, user_id_to_name)

        print("🔗 Tworzę relacje KNOWS...")
        session.write_transaction(create_connections, connections)

        print("🧭 Szukam najkrótszej ścieżki od Rafała do Barbary...")
        path = session.read_transaction(find_shortest_path)

        if path:
            print("✅ Najkrótsza ścieżka:")
            answer = ",".join(path)
            print(answer)
        else:
            print("❌ Nie znaleziono ścieżki!")

    driver.close()

    sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)
    response = sender.send(answer)


def run_secret():
    file_path = "s03e05/reversed_french_audio.mp3"  # lub pełna ścieżka

    client = OpenAIClient()  # zakłada, że masz zmienną środowiskową OPENAI_API_KEY
    text = client.transcribe_with_whisper(file_path)

    print("🔊 Transkrypcja audio:")
    print(text)