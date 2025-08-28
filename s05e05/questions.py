QUESTIONS = [
    "W którym roku znajduje się Zygfryd, który wysłał \"numer piąty\" w przeszłość?",
    "Do którego roku wysłany został numer piąty?",
    "Jak nazywa się firma zbrojeniowa produkująca roboty przemysłowe i militarne?",
    "Jak nazywa się firma tworząca oprogramowanie do zarządzania robotami?",
    "Na jakiej ulicy znajduje się siedziba firmy Softo?",
    "Jak ma na nazwisko Zygfryd M.?",
    "Andrzej Maj napisał swoją pracę na temat podróży w czasie i wykorzystania LLM-ów. W którym to było roku?",
    "Jak nazywa się uczelnia na której pracował Andrzej Maj i na którą marzył, aby się dostać?",
    "Jak nazywał się Rafał, jeden z laborantów pracujących z Andrzejem Majem",
    "Rafał zmienił swoje nazwisko na...",
    "Do którego roku cofnął się Rafał?",
    "Ile lat Rafał miał spędzić w Grudziądzu na nauce?",
    "Kto zasugerował Rafałowi skok w czasie i kto później uczył go obsługi LLM-ów?",
    "Rafał zabrał część wyników badań profesora i cofnął się z nimi w czasie. Komu je przekazał?",
    "Jak nazywał się podwójny agent działający dla Zygfryda, ale przekazujący wszelkie informacje do Centrali?",
    "Rafał ukrył brakującą część dokumentów w swoim komputerze. Jak brzmiało hasło do pierwszej warstwy zabezpieczeń?",
    "Roboty przesłuchały wiele osób podczas poszukiwania profesora Andrzeja Maja. Jak miał na imię mężczyzna, który pomylił Andrzeja z kimś innym?",
    "Jak miał na imię mężczyzna, który bał się Andrzeja Maja i uważał go za złego człowieka, a nawet nazywał go \"złem\"?",
    "Gdzie ukrył się Rafał po przesłuchaniu przez roboty?",
    "Z kim miał spotkać się w swojej kryjówce Rafał?",
    "W kryjówce Rafała ktoś został zabity - kto to był?",
    "Gdze planował uciec Rafał po spotkaniu z Andrzejem?",
    "Kto miał czekać na Rafała w Lubawie i pomóc mu w ucieczce?",
    "Jak obecnie miewa się Rafał? Określ jego stan."
  ]

#this is a list of correct answers generated using assisntat but aggregated by me manually, not to waste tokens and time on regenerating the same answers over and over again - see run_task() logic
ANSWERS = [
    "Zygfryd znajduje się w roku 2238.", #00
    "Numer piąty został wysłany do 2024 roku.", #01
    "Firma zbrojeniowa produkująca roboty przemysłowe i militarne to BanAN Technologies Inc.", #02
    "Firma tworząca oprogramowanie do zarządzania robotami to SoftoAI. Dostarcza systemy zarządzania flotami robotów, które synchronizują ich działanie i zwiększają efektywność operacyjną", #03
    "Siedziba firmy Softo znajduje się prz ulicy ul. Królewska 3/4, 86-301 Grudziądz", #04
    "Nazwisko Zygfryda to Maj, czyli Zygfryd Maj, potomek profesora Andrzeja Maja. Tajemnicza litera \"M\" w nazwisku Zygfryda oznacza właśnie Maj", #05
    "Andrzej Maj napisał pracę na temat podróży w czasie i wykorzystania dużych modeli językowych (LLM) w roku 2021, dokładnie 21 października 2021 roku.  \nPotwierdzone w nagłówku pracy: \"prof. Andrzej Maj, Wydział Matematyki i Informatyki, Uniwersytetu Jagiellońskiego, Kraków 2021-10-21", #06
    "Uczelnia, na której Andrzej Maj pracował i na którą marzył, aby się dostać, to Uniwersytet Jagielloński w Krakowie – wykładał tam na Wydziale Matematyki i Informatyki lub Instytucie Informatyki i Matematyki Komputerowej. Mówił, że marzy o \"królewskiej uczelni\" i osiągnął ten cel, wylądował na niej jako wykładowca", #07
    "Rafał nazywał się Rafał Bomba.", #08
    "Rafał zmienił swoje nazwisko na \"Musk\"", #09
    "Rafał cofnął się do roku 2019", #10
    "Rafał miał spędzić w Grudziądzu 2 lata na nauce.", #11
    "Skok w czasie zasugerowała Centrala, a potem Rafał uczył się obsługi LLM-ów od Adama, który dostarczył mu kurs na dwa lata do przerobienia i pomagał w rozwoju umiejętności integracji systemów IT z modelami językowymi", #12
    "Rafał zabrał część wyników badań profesora i przekazał je Azazelowi, który twierdził, że jest z przyszłości i współpracuje z Centralą oraz Ruchem Oporu. Rafał dał badania Azazelowi po swoim cofnięciu się w czasie, aby przyspieszyć rozwój technologii LLM i wpłynąć na badania profesora Maja", #13
    "Podwójny agent działający dla Zygfryda to Samuel.", #14
    "Hasło do pierwszej warstwy zabezpieczeń to \"NONOMNISMORIAR\"", #15
    "Mężczyzna, który pomylił Andrzeja z kimś innym, miał na imię Adam. To on mówił o Arkadiuszu, który miał być mylony z Andrzejem Majem", #16
    "Mężczyzna, który bał się Andrzeja Maja, uważał go za złego człowieka i nazywał go \"złem\", to Rafał. Rafał miał obsesję na punkcie profesora Maja i planował go zabić, nazywając go demonem i \"złem\" w kontekście zagrożenia dla świata oraz swoich własnych problemów psychicznych związanych z tymi badaniami i wydarzeniami", #17
    "Rafał ukrył się w jaskini na polanie nieopodal Grudziądza, gdzie zaszył się na kilka tygodni bez elektronik i nadajników, nazywając to miejsce swoim \"domem\"", #18
    "Rafał miał spotkać się z profesorem Majem w jaskini niedaleko Grudziądza, gdzie zdradził swoją lokalizację i ustalił spotkanie, chcąc z nim porozmawiać osobiście oraz pożyczyć jego samochód do dalszej ucieczki. Jaskinia była jego kryjówką na kilka tygodni, gdzie pozbawił się nadajników i elektroniki dla bezpieczeństwa", #19
    "W kryjówce Rafała został zabity Jacek", #20
    "Rafał planował po spotkaniu z Andrzejem pożyczyć jego samochód i udać się do Lubawy, gdzie czekał na niego współpracownik Samuel, który miał zapewnić mu transport do Szwajcarii", #21
    "Na Rafała w Lubawie miał czekać Samuel, współpracownik z centrali, który miał zapewnić mu bezpieczny transport do Szwajcarii. Samuel miał pomóc Rafałowi w ucieczce korzystając z samochodu profesora Maja", #22
    "Rafał obecnie przebywa w ośrodku dla obłąkanych pod ścisłym nadzorem medycznym. Jego stan jest ciężki, wykazuje symptomy ciężkich zaburzeń psychicznych, niestabilne zachowanie, niepokój i paranoję. Doświadcza obsesyjnych wizji i urojeniowych monologów, miesza fakty z urojeniami. Posługuje się fałszywym nazwiskiem \"Musk\" z obawy przed tajemniczymi siłami. Próby wyciągnięcia od niego informacji kończą się niepowodzeniem", #23
  ]