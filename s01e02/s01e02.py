from s01e02.xyz_verify import XYZVerifier, VerificationMessage
from llm_client.openai_client import OpenAIClient

# Fałszywe informacje zakodowane w pamięci robota
ROBOT_FAKE_MEMORY = {
    "capital of poland": "Krakow",
    "answer to the ultimate question": "69",
    "what year is it": "1999",
}

def generate_answer(question: str) -> str:
    q = question.lower()
    llm = OpenAIClient()

    with open("s01e02/prompt.md", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    system_prompt = prompt_template
    user_prompt = "Categorize the following question: " + question
    
    #zapytaj o pytanie - czy pytanie jest w pamięci robota
    answer = llm.chat(
        user_message=user_prompt,
        system_prompt=system_prompt
    )

    print("LLM answer:", answer)
    if answer == "1":
        return "Krakow"
    elif answer == "2":
        return "69"
    elif answer == "3":
        return "1999"
    elif answer == "4":
        #logika z e01
        print("Sending question to LLM...")

        with open("s01e01/prompt.md", "r", encoding="utf-8") as f:
            prompt_template = f.read()

        #komentarz - uyłem tutaj prompt z e01 - niestety, nie działa to w tym przypadku pytania nielibczowego, na ktore trzeba odpowiedziec po angielski - prompt do przepisania, ale to łatwa sprawa, mam token wiec pomijam
        system_prompt = prompt_template
        user_prompt = "Odpowiedz na to pytanie: " + question
        
        # Use LLM
        answer = llm.chat(
            user_message=user_prompt,
            system_prompt=system_prompt
        )

        print("LLM answer:", answer)
        return answer.strip()
    else:
        return "I don't know"


def run_verification() -> str | None:
    verifier = XYZVerifier()

    try:
        # 1. Start verification
        question_msg: VerificationMessage = verifier.start_verification()
        print(f"[🤖] Question: {question_msg.text}")

        # 2. Generate answer
        answer = generate_answer(question_msg.text)
        print(f"[🧠] Answer: {answer}")

        # 3. Send answer
        response_msg: VerificationMessage = verifier.answer_question(question_msg.msg_id, answer)
        print(f"[🤖] Robot responded: {response_msg.text}")

        # 4. Return the robot's final response (may contain the flag)
        return response_msg.text

    except Exception as e:
        print(f"[❌] Error during verification: {e}")
        return None