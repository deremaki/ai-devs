import os, json, requests, re, logging


from dotenv import load_dotenv

from llm_client.openai_client import OpenAIClient
from utils.answer_sender import AnswerSender

from s05e05.questions import QUESTIONS, ANSWERS

load_dotenv()

API_KEY = os.getenv("C3NTRALA_API_KEY")
TASK_NAME = "story"

ASSISTANT_ID = "asst_MZRs7WPGgrBdUbLlqs1OrlNB"

sender = AnswerSender(task_name=TASK_NAME, api_key=API_KEY)
llm = OpenAIClient()


def answer_question(question):

    thread = llm.client.beta.threads.create()
    llm.client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=question
    )
    run = llm.client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID
    )
    messages = llm.client.beta.threads.messages.list(thread_id=thread.id)

    for m in messages.data:
        if m.role == "assistant":
            answer = m.content[0].text.value


    debug_message = f"""
    QUESTION:   {question}
    ANSWER:     {answer}  """

    print(debug_message)
    return answer


def run_task():

    question_list = QUESTIONS

    answers_list = ANSWERS

    final_answers = []

    for i in range(len(answers_list)):
        if answers_list[i] == "":
            print("[INFO] Question "+str(i)+": We don't have correct info here - asking LLM:")
            answer = answer_question(question_list[i])
            final_answers.append(answer)
        else:
            print("[INFO] Question "+str(i)+": We already have a good answer here - skipping...")
            final_answers.append(answers_list[i])
        

    print("[ANSWER] Sending answers to Centrala…")
    resp = sender.send(final_answers) 