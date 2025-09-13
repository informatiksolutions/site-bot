import re
INTENT_RULES = [
    (r"\b(preis|preise|kosten|tarif)\b", "preise"),
    (r"\b(kontakt|telefon|email|anschrift)\b", "kontakt"),
    (r"\b(termin|beratung|angebot)\b", "termin"),
    (r"\b(service|leistung|it|support|wartung|cloud|backup)\b", "leistungen"),
]

def detect_intent(q: str) -> str:
    low = q.lower()
    for patt, name in INTENT_RULES:
        if re.search(patt, low):
            return name
    return "suche"
