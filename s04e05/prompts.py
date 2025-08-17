SYSTEM_PROMPT = (
    "Jesteś asystentem ekstrakcji faktów. Odpowiadasz WYŁĄCZNIE na podstawie "
    "dostarczonego kontekstu (NOTATNIK RAFAŁA). Zwracasz zwięzłą odpowiedź po polsku, "
    "bez komentarzy, bez cytatów, bez dopisków."
)

def user_prompt_first(notes_text: str, qid: str, question: str) -> str:
    return (
        "KONTEKST (NOTATNIK RAFAŁA):\n<<<\n"
        f"{notes_text}\n"
        ">>>\n\n"
        f"PYTANIE [ID={qid}]: {question}\n\n"
        "Zwróć TYLKO zwięzłą finalną odpowiedź (bez cudzysłowów, bez dodatkowych słów)."
    )

def user_prompt_retry(notes_text: str, qid: str, question: str, prev_answer: str, hint: str) -> str:
    return (
        "KONTEKST (NOTATNIK RAFAŁA):\n<<<\n"
        f"{notes_text}\n"
        ">>>\n\n"
        f"PYTANIE [ID={qid}]: {question}\n\n"
        f"Twoja poprzednia odpowiedź brzmiała: «{prev_answer}» i była błędna.\n"
        f"Podpowiedź (hint): «{hint}».\n"
        f"Spróbuj ponownie. NIE używaj odpowiedzi «{prev_answer}».\n\n"
        "Zwróć TYLKO zwięzłą finalną odpowiedź (bez cudzysłowów, bez dodatkowych słów)."
    )
