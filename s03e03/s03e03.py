import os
import requests
from dotenv import load_dotenv
from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
API_URL = "https://c3ntrala.ag3nts.org/apidb"

llm = OpenAIClient()

def query_api(sql_query):
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

def llm_extract_table_names(json_data):
    prompt = f"""
Below is json with database tables list. 
Exctract from it names of tables (values of "Tables_in_banan") as a list of strings. YOU MAY NOT RETURN ANYTHING ELSE!
JSON:
{json_data}
"""
    response = llm.chat(user_message=prompt)
    print(f"[LLM] Extracted table names: {response}")
    return eval(response) if response.startswith("[") else []

def llm_select_relevant_tables(table_names):
    prompt = f"""
Spośród poniższych tabel wybierz te, które mogą być potrzebne do wykonania zapytania:
"Zwróć id datacenterów, które są aktywne, ale ich menadżerowie (użytkownicy) są nieaktywni."
Zwróć tylko listę stringów z nazwami tabel.

Dostępne tabele:
{table_names}
"""
    response = llm.chat(user_message=prompt)
    print(f"[LLM] Relevant tables selected: {response}")
    return eval(response) if response.startswith("[") else []

def llm_generate_sql(context):
    schema_snippets = "\n\n".join([f"Table {table} schema:\n{schema}" for table, schema in context.items()])
    prompt = f"""
You are an SQL expert. Based on the following table definitions, write a single SQL query that returns the DC_IDs (datacenter id) of ACTIVE datacenters that are managed by users who are currently inactive in the users table.
Strictly follow the schema provided. 
RETURN ONLY THE SQL. Do not explain or comment anything.

{schema_snippets}
"""
    print("[LLM] Sending prompt to OpenAI for SQL generation...")
    sql = llm.chat(user_message=prompt)
    print(f"[LLM] Generated SQL: {sql}")
    return sql


def extract_ids(json_data):
    prompt = f"""
Below is json with datacenter ids list (dc_id). 
Exctract from it the ids of datacenter (values of "dc_id") as a list of strings. YOU MAY NOT RETURN ANYTHING ELSE!
JSON:
{json_data}
"""
    response = llm.chat(user_message=prompt)
    print(f"[LLM] Extracted datacenters ids: {response}")
    return eval(response) if response.startswith("[") else []

def run_task():
    context = {}

    print("[INFO] Starting task S03E03 - database")

    # Step 1: get table list
    print("[STEP] Retrieving list of tables...")
    show_tables_result = query_api("SHOW TABLES;")
    context["tables_json"] = show_tables_result

    table_names = llm_extract_table_names(show_tables_result)
    #relevant_tables = llm_select_relevant_tables(table_names)
    relevant_tables = table_names

    # Step 2: get CREATE TABLE for relevant tables
    for table in relevant_tables:
        print(f"[STEP] Retrieving schema for table: {table}")
        result = query_api(f"SHOW CREATE TABLE {table};")
        schema = result['reply'][0]['Create Table']
        if not schema:
            print(f"[ERROR] Failed to retrieve schema for table: {table}")
            return
        context[table] = schema
        print(f"[INFO] Schema for {table}:{schema}")


    # Step 3: Generate SQL from schemas
    print("[STEP] Generating SQL with LLM...")
    sql = llm_generate_sql(context)

    # Step 4: Execute SQL
    print("[STEP] Executing generated SQL...")
    result = query_api(sql)

    # Step 5: Extract DC IDs
    print("[STEP] Extracting datacenter IDs from result...")
    ids = extract_ids(result)

    if not ids:
        print("[WARNING] No datacenter IDs found. Aborting task.")
        return

    payload = {
        "task": "database",
        "apikey": API_KEY,
        "answer": ids
    }

    # Step 6: Send final answer
    print(f"[STEP] Sending final answer: {payload}")
    sender = AnswerSender(task_name="database", api_key=API_KEY)
    sender.send(ids)
    print("[INFO] Task completed successfully.")


def run_secret():
    show_tables_result = query_api("SHOW TABLES;")
    result = query_api(f"SHOW CREATE TABLE correct_order;")
    schema = result['reply'][0]['Create Table']

    sql = "SELECT base_id, letter, weight FROM correct_order ORDER BY weight;"
    
    data = query_api(sql)

    secret_flag = ''.join(sorted(data['reply'], key=lambda x: int(x['weight']))[i]['letter'] for i in range(len(data['reply'])))

    print(secret_flag)
