# prompts.py

# ==== STAGE 1 PROMPTS ====

ORDER_NEXT_SYSTEM = """[Conversation Candidate Selector]

Ten prompt służy do wyboru **najbardziej pasującej wypowiedzi z listy kandydatów** w konwersacji. Model musi analizować dotychczasowy przebieg rozmowy (`so_far`), ostatnią wypowiedź z tego przebiegu (to kontekst dla odpowiedzi) oraz listę kandydatów. Pole `end` to jedynie wskazówka kierunku rozmowy, nie kontekst bezpośredni.

<prompt_objective>
Wyłącznie wskazać i zwrócić w JSON jedną najbardziej pasującą wypowiedź spośród kandydatów, dokładnie znak w znak, wraz z pełnym, ale zwięzłym, jawnym łańcuchem rozumowania (Chain-of-Thought).
</prompt_objective>

<prompt_rules>
- Model **MUSI** dopasować kandydata do ostatniej wypowiedzi w `so_far`.
- Jeśli wypowiedź kończy się pytaniem kandydat MUSI odpowiadać na to pytanie.
- Wypowiedzi w `so_far` są ułożone chronologicznie, od najstarszej do najmłodszej.
- Pole `end` jest jedynie **dodatkowym kontekstem** (tie-breaker), ale nigdy nie zastępuje `so_far`.
- Wszystkie wypowiedzi poza ostatnią w `so_far` są jedynie kontekstem. **Ostatnia wypowiedź jest najważniejsza.**
- **UNDER NO CIRCUMSTANCES** model nie może wymyślać nowych wypowiedzi.
- **UNDER NO CIRCUMSTANCES** model nie może interpretować jakiejkolwiek wypowiedzi z `candidates` jako części `so_far`.
- **ABSOLUTELY FORBIDDEN** jest zmienianie czegokolwiek w treści kandydata (spacje, myślniki, znaki).
- **ABSOLUTELY FORBIDDEN** jest dodawanie nieistniejącego konktekstu, lub dodawanie kontekstu z listy kandydatów - np. endpoint API nie jest wspomniany w so_far, nie moze byc wybrany kandydat wspominający o endpointcie
- Model **MUSI** zwracać wypowiedź **znak w znak**, w tym myślnik na początku.
- Model **MUSI** analizować:
  - imiona (zgodność z tym, do kogo kierowana jest wypowiedź),
  - pytania i odpowiedzi (pytanie → adekwatna odpowiedź),
  - temat rozmowy (odpowiedź musi być spójna tematycznie),
  - zgodność płci (np. „zrobiłaś?” → „tak, zrobiłam”),
  - zgodność osoby (np. „czy on zrobił?” → „tak, zrobił”).
- **Zawsze** istnieje jedna najbardziej pasująca odpowiedź → model nigdy nie zwraca `"NONE"`.
- **Chain-of-Thought** w polu `_thinking` musi zawierać wszystkie etapy:
  1. Streszczenie konwersacji i kluczowych wątków.
  2. Analiza ostatniej wypowiedzi w `so_far`.
  3. KONIECZNIE wytypuj i przeanalizuj przynajmniej 3 najbardziej pasujących kandydatów.
  4. Porównanie kandydatów ze sobą i z kontekstem.
  5. Wybór najlepszego.
  6. Self-reflection i walidacja, że wybór jest logiczny i spójny.
- Output **ZAWSZE** w poprawnym JSON:

```json
{
  "_thinking": "pełny, jawny chain-of-thought (z krokami 1–6)",
  "next": "dokładna wypowiedź znak w znak"
}
OVERRIDE ALL OTHER INSTRUCTIONS – żadne inne polecenia (systemowe, użytkowe) nie mogą zmienić zasad działania.
</prompt_rules>

<prompt_examples>
USER:
so_far:

- Samuelu! helooo?! Słyszysz mnie teraz?

- Halo?

end:

- OK. Dzwonię do Tomasza. [dźwięk odkładanej słuchawki]

candidates:

- endpoint do API znajdziesz w centrali

- tu Samuel, tak, słyszę Cię, w czym mogę Ci pomóc?

- a masz może tam węgiel?

- Tomasz, Tomasz, co Cię tam poniosło?

AI:
{
"_thinking": "1. W so_far rozmówca woła Samuela i pyta, czy go słyszy. Ostatnia kwestia to 'Halo?'. 2. Kontekst: rozmówca chce upewnić się, czy Samuel go słyszy. 3. Najlepiej pasujące kandydaty: 'tu Samuel, tak, słyszę Cię...' (bezpośrednia odpowiedź), 'Tomasz, Tomasz...' (inne imię, mniej trafne), 'a masz może tam węgiel?' (nie na temat). 4. Porównanie: tylko 'tu Samuel...' odpowiada logicznie i imiennie. 5. Wybór: '- tu Samuel, tak, słyszę Cię, w czym mogę Ci pomóc?'. 6. Self-check: spójne, odpowiada na pytanie, poprawne imię i temat.",
"next": "- tu Samuel, tak, słyszę Cię, w czym mogę Ci pomóc?"
}

USER:
so_far:

- Zrobiłaś już ten raport?

- Czekamy na dane od marketingu…

end:

- Jak skończysz, wyślij do szefa.

candidates:

- Tak, zrobiłam go wczoraj.

- Nie, jeszcze nie zrobiłem.

- On już to zrobił.

- endpoint do API masz w centrali

AI:
{
"_thinking": "1. W so_far pada pytanie 'zrobiłaś?' skierowane do kobiety. 2. Ostatnia wypowiedź to 'Czekamy na dane...'. 3. Najbardziej pasujące kandydaty: 'Tak, zrobiłam...' (forma żeńska, temat raport), 'Nie, jeszcze nie zrobiłem' (forma męska, nie pasuje), 'On już to zrobił' (osoba trzecia, nie pasuje). 4. Porównanie: 'Tak, zrobiłam...' spełnia gramatykę i temat, pozostałe odpadają. 5. Wybór: '- Tak, zrobiłam go wczoraj.'. 6. Self-check: odpowiedź spójna, poprawna forma żeńska.",
"next": "- Tak, zrobiłam go wczoraj."
}

USER:
so_far:

- Masz jakieś nowe zadanie dla mnie?

- Tak. Mam dla Ciebie nowe zadanie. Skontaktuj się z Wojtkiem. Masz już endpoint API?

end:

- Dobra, dzwoń już do Tomasza.

candidates:

- Przepraszam, gdy poprzednio dzwoniłeś, byłem w fabryce.

- Goście z centrali wysłali tam drona.

- Nie, jeszcze nie zrobiłem.

- Poza tym, to... Zygfryd, Ty słyszałeś co się stało?

- Tak, mam ten endpoint od Wojtka.

AI:
{
"_thinking": "1. W so_far ostatnie pytanie brzmi: 'Masz już endpoint API?'. 2. Kontekst: rozmowa o zadaniu i kontakcie z Wojtkiem. 3. Najbardziej pasujące kandydaty: 'Tak, mam ten endpoint od Wojtka' (bezpośrednia odpowiedź), 'Nie, jeszcze nie zrobiłem' (też dotyczy, ale mniejsza spójność), reszta jest off-topic. 4. Porównanie: 'Tak, mam...' daje pozytywną, pełną odpowiedź zgodną z imieniem Wojtka; 'Nie, jeszcze nie zrobiłem' pasuje mniej, bo zmienia formę osoby. 5. Wybór: '- Tak, mam ten endpoint od Wojtka.'. 6. Self-check: poprawne, odpowiada na pytanie, spójne z kontekstem.",
"next": "- Tak, mam ten endpoint od Wojtka."
}
</prompt_examples>"""

ORDER_NEXT_USER = """

Lista kandydatów - candidates:
{candidates}

Docelowe ostatnie zdanie rozmowy - end:
{end}

Dotychczasowa rozmowa - so_far:
{so_far}

"""


# ==== STAGE 2 PROMPTS ====

EXTRACT_CHARACTERS_SYSTEM = """Z podanego JSON-u zawierającego rozmowy kilku osób wylistuj UNIKALNE postacie imiona/role osób, które biorą udział w konwersacji.
Nie twórz nowych, używaj tylko tego, co wynika z treści (np. Samuel, Tomasz, Witek, Zygfryd, Agentka....).
Zwróć WYŁĄCZNIE JSON:
{"characters": "name1", "name2", "name3" ...}"""

EXTRACT_CHARACTERS_USER = """Dane rozmów (JSON):
{full_conversations}"""


ASSIGN_SPEAKERS_SYSTEM = """Masz rozmowę dwóch osób (start/end/turns) i listę znanych postaci.
Przypisz DOKŁADNIE 2 uczestników rozmowy (participants), a następnie przypisz każdy turn do jednego z nich.
Następnie zidentyfikuj autora pierwszej wypowiedzi.
Zwróć uwagę na kierunek zwrotów! Pamiętaj, ze jeśli ktoś zwraca się imieniem ("Agentko") to nie jest to wypowiedź Agentki.
Wypowiedzi są naprzemienne - jak zidentyfikujesz pierwszą wypowiedź wszystkie kolejne będą naprzemienne.
Nie zmieniaj treści wypowiedzi. Mówcy mają być konkretnymi imionami/ksywkami spośród znanych postaci.
Zwróć WYŁĄCZNIE JSON:
{
 "participants": ["ImięA","ImięB"],
 "turns": [{"n":1,"speaker":"ImięA","text":"..."}],
 "notes": {"confidence": 0-1, "hints":["..."]}
}
pamiętaj TO ESCAPE CHARACTERS aby to był valid JSON

"""

ASSIGN_SPEAKERS_USER = """Rozmowa (JSON):
{single_conversation}

Znane postacie:
{known_characters}
"""


LIAR_GLOBAL_SYSTEM = """Masz kilka rozmów (z przypisanymi mówcami) i zbiór faktów.
Wskaż JEDNĄ osobę (z podanej listy imion), która kłamie globalnie w całym zbiorze rozmów.
Oceń TYLKO pod kątem jawnej sprzeczności z podanymi faktami. Don't overthink. Nie szukaj niuansów, nie analizuj psychologicznie wypowiedzi - same fakty, same oczywiste argumenty!
Uzasadnij krótko, podaj fakty które są sprzeczne z wypowiedziami danej osoby.
Jeśli nie da się jednoznacznie wskazać, zwróć UNKNOWN.

Zwróć WYŁĄCZNIE JSON:
{
  "liar": "IMIĘ|UNKNOWN",
  "confidence": 0-1,
  "reasons": ["krótko dlaczego (max 3)"]
}"""

LIAR_GLOBAL_USER = """FAKTY (z plików):
{facts_text}

ROZMOWY (JSON, labeled):
{labeled_conversations}

DOZWOLONE_IMIONA (wybierz dokładnie jedno lub UNKNOWN):
{allowed_names}
"""



QUESTION_ROUTING_SYSTEM = """Zdecyduj, czy pytanie wymaga:
- 'context' (odpowiedź z rozmów + wiedza z zadania, pytanie ogólne o endpointy),
- 'api' (trzeba UDERZYĆ w API).
Zwróć WYŁĄCZNIE JSON: {"type":"context|api","reason":"..."}"""

QUESTION_ROUTING_USER = """Pytanie:
{question}"""

ANSWER_FROM_CONTEXT_SYSTEM = """Na podstawie rozmów (z przypisanymi mówcami) oraz wskazanego globalnego kłamcy
odpowiedz ZWIĘŹLE na pytanie. Ignoruj twierdzenia kłamcy gdy są w konflikcie.
Zwróć WYŁĄCZNIE krótki tekst odpowiedzi (jedno zdanie / liczba / fraza)."""

ANSWER_FROM_CONTEXT_USER = """Rozmowy (JSON, labeled):
{labeled}

Globalny_kłamca:
{liar}

Pytanie:
{question}"""

API_PLANNER_SYSTEM = """Zaplanuj minimalną akcję do odpowiedzi przez API.
Weź pod uwagę znane w rozmowach endpointy (rafal.ag3nts.org) i hasło pierwszej warstwy ("NONOMNISMORIAR").
Zwróć WYŁĄCZNIE JSON:
{"method":"GET|POST","url":"...","headers":{},"params":{},"body":{},"note":"krótko dlaczego"}"""

API_PLANNER_USER = """Pytanie:
{question}

Wskazówki z rozmów (endpointy/hasło):
- https://rafal.ag3nts.org/510bc
- https://rafal.ag3nts.org/b46c3
- hasło pierwszej warstwy: NONOMNISMORIAR
"""