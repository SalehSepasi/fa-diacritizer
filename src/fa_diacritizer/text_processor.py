
def remove_diacritics(text: str) -> str:

    DIACRITICS = {
    "َ",  # FATHA
    "ُ",  # DAMMA
    "ِ",  # KASRA
    "ْ",  # SOKUN
    "ّ",  # SHADDA
    "ً",  # FATHATAN
    "ٌ",  # DAMMATAN
    "ٍ",  # KASRATAN
    }

    return "".join(
            ch for ch in text
            if ch not in DIACRITICS
        )
    