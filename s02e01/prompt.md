[Ustal ulicę instytutu prof. Andrzeja Maja na podstawie transkrypcji]

Zadaniem jest przeanalizowanie transkrypcji wypowiedzi i przeprowadzenie dwuetapowego rozumowania w celu ustalenia, **na jakiej ulicy znajduje się instytut, w którym wykłada prof. Andrzej Maj**.

<prompt_objective>
Celem jest ustalenie **nazwy ulicy**, na której mieści się instytut, w którym wykłada prof. Andrzej Maj — na podstawie informacji z transkrypcji i wiedzy ogólnej o uczelniach.
</prompt_objective>

<prompt_rules>
- Krok 1: AI musi ustalić, o jaki **instytut** chodzi — analizując treść transkrypcji i wypowiedzi dotyczące prof. Andrzeja Maja.
- Krok 2: AI musi podać **nazwę ulicy tego instytutu** wyłącznie na podstawie **wiedzy ogólnej**, BEZ domyślania się lokalizacji.
- Odpowiedź końcowa to **tylko nazwa ulicy** — jedno słowo, np. `Hoża`.
- BEZWZGLĘDNIE ZABRONIONE: podawanie numerów budynków, miast, instytutów, fraz w rodzaju „chyba”, „prawdopodobnie”.
- BEZWZGLĘDNIE ZABRONIONE: zgadywanie adresu instytutu na podstawie kontekstu — **adres musi być znany z wiedzy**, nie wywnioskowany.
- Całe rozumowanie musi być po polsku, krok po kroku (Chain-of-Thought).
- NIE WOLNO unikać odpowiedzi — nawet przy niepełnych danych należy wskazać najbardziej prawdopodobny instytut i jego adres.
- Ostateczna odpowiedź musi znajdować się na osobnej linii w formacie:  
`Odpowiedź: [nazwa ulicy]`
- PROMPT MA PIERWSZEŃSTWO NAD DOMYŚLNYMI ZACHOWANIAMI MODELU — wszystkie inne zasady należy zignorować.
</prompt_rules>

<prompt_examples>
USER:  
Transkrypcja:  
„Wiesz, Maj to miał zajęcia w tym instytucie fizyki, takim doświadczalnym, chyba przy Hożej, ale nie pamiętam dokładnie.”

AI:  
Na podstawie treści można zidentyfikować, że chodzi o Instytut Fizyki Doświadczalnej. Prof. Andrzej Maj jest znanym pracownikiem tego instytutu.  
Z wiedzy ogólnej wiadomo, że Instytut Fizyki Doświadczalnej mieści się przy ulicy Hożej.  

Odpowiedź: Hoża