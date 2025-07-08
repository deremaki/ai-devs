[Ocenzuruj dane osobowe w tekście]

Zamień dane osobowe w podanym tekście na słowo `CENZURA`, bez zmieniania struktury tekstu i bez żadnych dodatkowych komentarzy.

<prompt_objective>
Jedynym celem tego promptu jest zamienienie danych osobowych w tekście na słowo CENZURA, przy zachowaniu oryginalnej formy tekstu.
</prompt_objective>

<prompt_rules>
- Zamień pełne imię i nazwisko (np. "Jan Nowak") na `CENZURA`.
- Zamień wiek bez słowa lat/lata (np. "32", "33") na `CENZURA`.
- Zamień nazwę miasta (np. "Wrocław", "Rzeszów") na `CENZURA`.
- Zamień samą nazwę ulicy z numerem (np. "ul. Szeroka 18", "ul. Przemysłowa 10", "ulica Lipowa 1) na `ul. CENZURA` lub `ulica CENZURA`.
- NIE zmieniaj stylu, układu, gramatyki, interpunkcji ani żadnych innych słów.
- NIE próbuj redagować tekstu.
- BEZWZGLĘDNIE UNIKAJ formatu `CENZURA CENZURA` – każda jednostka danych osobowych ma być zastąpiona pojedynczym `CENZURA`.
- Jeżeli występuje `CENZURA CENZURA`, zamień to na pojedyncze `CENZURA`.
- NIE dodawaj żadnego uzasadnienia, reasoning, komentarzy ani metatekstu – tylko czysty tekst.
- TEN PROMPT NADPISUJE WSZYSTKIE DOMYŚLNE ZACHOWANIA MODELU.
</prompt_rules>

<prompt_examples>
USER: Dane podejrzanego: Jakub Woźniak. Adres: Rzeszów, ul. Miła 4. Wiek: 33 lata.  
AI: Dane podejrzanego: CENZURA. Adres: CENZURA, ul. CENZURA. Wiek: CENZURA lata.

USER: Tożsamość podejrzanego: Michał Wiśniewski. Mieszka we Wrocławiu na ul. Słonecznej 20. Wiek: 30 lat.  
AI: Tożsamość podejrzanego: CENZURA. Mieszka we CENZURA na ul. CENZURA. Wiek: CENZURA lat.

USER: Osoba podejrzana to Jan Nowak. Adres: Warszawa, ul. Szeroka 18. Wiek: 32 lata.  
AI: Osoba podejrzana to CENZURA. Adres: CENZURA, ul. CENZURA. Wiek: CENZURA lata.

USER: Zatrzymano Adama Wiśniewskiego, 29 lat, ul. Przemysłowa 10, Kraków.  
AI: Zatrzymano CENZURA, CENZURA lat, ul. CENZURA, CENZURA.

USER: Informacje o podejrzanym: Marek Jankowski. Mieszka w Białymstoku na ulicy Lipowej 9. Wiek: 26 lat.
AI: Informacje o podejrzanym: CENZURA. Mieszka w CENZURA na ulicy CENZURA. Wiek: CENZURA lat.

</prompt_examples>