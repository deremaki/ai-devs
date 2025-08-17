import os, json, re, time, pathlib, requests
from typing import Dict, Tuple, Optional

OUT_DIR = pathlib.Path("s04e05/out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_notes_text(path: str = "s04e05/notes.txt") -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_questions_url() -> str:
    # jeśli klucz do danych = API key, użyj C3NTRALA_API_KEY; w innym wypadku ustaw NOTES_DATA_KEY
    data_key = os.getenv("NOTES_DATA_KEY") or os.getenv("C3NTRALA_API_KEY")
    if not data_key:
        raise RuntimeError("Brak NOTES_DATA_KEY/C3NTRALA_API_KEY do pobrania notes.json")
    return f"https://c3ntrala.ag3nts.org/data/{data_key}/notes.json"

def fetch_questions(timeout: int = 20) -> Dict[str, str]:
    url = build_questions_url()
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    # sanity: upewnij się, że klucze są "01".."05"
    want = {f"{i:02d}" for i in range(1, 6)}
    missing = want - set(data.keys())
    if missing:
        raise ValueError(f"Brak pytań dla kluczy: {sorted(missing)}")
    return {k: str(v) for k, v in data.items()}

def normalize_answer(s: str) -> str:
    s = s.strip()
    # usuń otaczające cudzysłowy jeśli model je dorzuci
    if len(s) >= 2 and ((s[0] == s[-1] == '"') or (s[0] == s[-1] == "'")):
        s = s[1:-1].strip()
    # pojedyncza linia
    return " ".join(s.split())

def send_report(apikey: str, answers: Dict[str, str], timeout: int = 30) -> dict:
    payload = {
        "task": "notes",
        "apikey": apikey,
        "answer": answers
    }
    r = requests.post("https://centrala.ag3nts.org/report",
                      headers={"Content-Type": "application/json; charset=utf-8"},
                      data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                      timeout=timeout)
    try:
        resp = r.json()
    except Exception:
        resp = {"status_code": r.status_code, "text": r.text}
    # log
    stamp = str(int(time.time()))
    (OUT_DIR / f"report-response-{stamp}.json").write_text(json.dumps(resp, ensure_ascii=False, indent=2), encoding="utf-8")
    return resp

_QID_RE = re.compile(r"question\s+(\d{2})", re.IGNORECASE)

def parse_incorrect_info(resp: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Zwraca (qid, hint, debug_sent_answer) lub (None, None, None) gdy brak danych.
    Oczekiwany format jak w przykładzie:
    {
      "code": -340,
      "message": "Answer for question 01 is incorrect",
      "hint": "...",
      "debug": "You sent: 2018"
    }
    """
    if not isinstance(resp, dict):
        return None, None, None
    message = str(resp.get("message", ""))
    m = _QID_RE.search(message)
    qid = m.group(1) if m else None
    hint = resp.get("hint")
    debug = resp.get("debug")
    # spróbuj wyciągnąć poprzednią odpowiedź z debugu
    prev = None
    if isinstance(debug, str):
        # najpierw po stałej frazie
        if "You sent:" in debug:
            prev = debug.split("You sent:", 1)[1].strip()
        else:
            # fallback: pierwsze słowo/linia
            prev = debug.strip().splitlines()[0].strip()
    return qid, hint, prev
