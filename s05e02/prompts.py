REFLECTION_SYSTEM = (
"Jesteś pomocnym, dokładnym planistą. Twoim zadaniem jest przekształcić zadanie użytkownika w plan działania."
)


REFLECTION_PROMPT = (
"""
Wejście:
- Zadanie użytkownika (po polsku):\n{task}


Zadania dla Ciebie:
1) Zidentyfikuj listę celów (kogo i co mamy ustalić; np. imiona osób, miasta itp.)
2) Określ jakie informacje są potrzebne i jak je uzyskać, biorąc pod uwagę dostępne narzędzia
3) Ułóż plan high-level (sekwencja kroków z użyciem narzędzi)
4) Zdefiniuj warunek zakończenia (co musi być znane, by odpowiedzieć)


Zwróć STRICT JSON, bez komentarzy i bez dodatkowego tekstu, z kluczami: cele, potrzebne_info, plan, osoby, miejsca, warunek_zakonczenia, notatki."
"""
)


DECIDE_SYSTEM = (
"Jesteś kontrolerem pętli agenta. Decydujesz, czy można zakończyć, czy trzeba użyć narzędzia."
)


DECIDE_PROMPT = (
"""
Kontekst:
- Plan (reflection):\n{reflection}
- Stan znanych danych (state):\n{state}
- Historia (skrócona):\n{short_history}


Pytanie:
- Czy jesteś absolutnie pewny ze mamy już wszystko, by odpowiedzieć zgodnie z planem? Jeśli TAK -> ready=true.
- Jeśli NIE -> wybierz jedno działanie z listy narzędzi: [GET_USER_ID, GET_GPS_LOCATION, LIST_USERS_IN_CITY]
i podaj minimalne argumenty.
LIST_USERS_IN_CITY - przyjmuje nazwę miasta i listuje USERów tam przebywających
GET_USER_ID - przyjmuje imie usera i zwraca userID
GET_GPS_LOCATION - przyjmuje userID oraz imie i zwraca lokalizacja (lat, log)


Zwróć STRICT JSON:
{
"ready": true | false,
"action": {
"tool": "GET_USER_ID" | "GET_GPS_LOCATION" | "LIST_USERS_IN_CITY",
"args": {"name"?: str, "user_id"?: str, "city"?: str},
"uzasadnienie": "..."
}
}
"""
)


VERIFY_SYSTEM = (
"Jesteś recenzentem odpowiedzi. Sprawdzasz zgodność z celem i wskazujesz braki."
)


VERIFY_PROMPT = (
"""
Plan (warunek zakończenia): {finish_condition}
Proponowana odpowiedź:\n{answer}


Zwróć STRICT JSON:
{"ok": true | false, "braki": ["..."]}
"""
)