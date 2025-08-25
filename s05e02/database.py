import os
import json
import string
import requests
from dotenv import load_dotenv


load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"


def query_database(sql_query):
    print(f"[QUERY] Executing SQL: {sql_query}")
    response = requests.post(API_URL, json={
        "task": "database",
        "apikey": API_KEY,
        "query": sql_query
    })
    response.raise_for_status()
    json_data = response.json()
    print(f"[RESPONSE] Received: {json_data}")
    return json_data

def show_tables():
    return query_database("SHOW TABLES;")

def show_table_by_name(table_name):
    return query_database(f"SHOW CREATE TABLE {table_name};")


def query_userID(username):
    username = username.upper()
    response = query_database(f"SELECT id AS userID FROM users WHERE username = '{username}';")
    user_id = response['reply'][0]['userID']
    return user_id