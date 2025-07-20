import os
import glob
import uuid
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from llm_client.openai_client import OpenAIClient
import requests

COLLECTION_NAME = "ai_devs-s03e02"
QDRANT_URL = "http://localhost:6333"
VECTOR_SIZE = 3072
EMBEDDING_MODEL = "text-embedding-3-large"
DATA_DIR = "s03e02/weapons_tests"


def prepare_qdrant():
    client = QdrantClient(url=QDRANT_URL)

    if COLLECTION_NAME not in [c.name for c in client.get_collections().collections]:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
        )

    return client


def embed_text(client: OpenAIClient, text: str) -> list[float]:
    response = client.client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


def index_documents(qdrant: QdrantClient, oai: OpenAIClient):
    files = glob.glob(os.path.join(DATA_DIR, "*.txt"))

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(file_path)
        date = filename.split(".")[0].replace("_", "-")

        vector = embed_text(oai, content)

        point = PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"date": date, "filename": filename}
        )

        qdrant.upsert(collection_name=COLLECTION_NAME, points=[point])

        print("Zaindeksowano plik: " + file_path)

    print(f"Zaindeksowano {len(files)} dokumentów.")


def query_question(qdrant: QdrantClient, oai: OpenAIClient, question: str) -> str:
    vector = embed_text(oai, question)

    search_result = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=vector,
        limit=1
    )

    if not search_result:
        raise Exception("Brak wyników!")

    return search_result[0].payload["date"]


def send_answer(apikey: str, date: str):
    url = "https://c3ntrala.ag3nts.org/report"
    payload = {
        "task": "wektory",
        "apikey": apikey,
        "answer": date
    }
    response = requests.post(url, json=payload)
    print(f"✅ Odpowiedź: {response.text}")
    return response


def run_task():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    task_api_key = os.getenv("C3NTRALA_API_KEY")
    if not task_api_key:
        raise ValueError("Brakuje zmiennej środowiskowej C3NTRALA_API_KEY")

    qdrant = prepare_qdrant()
    openai_client = OpenAIClient(api_key=api_key)

    index_documents(qdrant, openai_client)

    question = "W raporcie, z którego dnia znajduje się wzmianka o kradzieży prototypu broni?"
    result_date = query_question(qdrant, openai_client, question)

    send_answer(task_api_key, result_date)