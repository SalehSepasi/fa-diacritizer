
import re


ZWNJ = "\u200c"

# ---------------------------------------------------------------------------
# Normalization of characters and spaces
# ---------------------------------------------------------------------------
_CHAR_MAP = str.maketrans({
    "ي": "ی", "ى": "ی", "ك": "ک", "ة": "ه",
    "أ": "ا", "إ": "ا", "ٱ": "ا",
    "ـ": "",                                  
    "\u200d": "", "\u200e": "", "\u200f": "",  
    "\ufeff": "", "\u202a": "", "\u202b": "", "\u202c": "",
    "\u202d": "", "\u202e": "",
})
_DIACRITICS_RE = re.compile("[\u064B-\u0652\u0670]")


def normalize_chars(text: str, strip_diacritics: bool = True) -> str:
    """
    Unifying Arabic/Persian letters and removing invisible characters.
    If the text already had diacritics, we remove them so the model sees a 'raw' input.
    """
    text = text.translate(_CHAR_MAP)
    if strip_diacritics:
        text = _DIACRITICS_RE.sub("", text)
    return text


def normalize_whitespace(text: str) -> str:
    """
    It removes extra spaces, repeated half-spaces (ZWNJ), and a half-space with a space.
    """
    text = re.sub(r"[ \t\r\f\v\u00a0]+", " ", text)
    text = re.sub(f"{ZWNJ}+", ZWNJ, text)
    text = re.sub(f"[ \n]{ZWNJ}|{ZWNJ}[ \n]", " ", text)
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n+", "\n", text)
    return text.strip(f" {ZWNJ}")


# ---------------------------------------------------------------------------
# Digits
# ---------------------------------------------------------------------------
_DIGIT_MAP = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "0123456789" * 2)


def normalize_digits(text: str) -> str:
    """ convert Persian/Arabic digits to Latin,
        removing the thousands separator (1,500,000),
        convert the Arabic decimal separator (٫) to a dot.
    """
    text = text.translate(_DIGIT_MAP)
    text = re.sub(r"(?<=\d)٫(?=\d)", ".", text)
    text = re.sub(
        r"(?<!\d)\d{1,3}(?:[,٬]\d{3})+(?!\d)",
        lambda m: re.sub(r"[,٬]", "", m.group()),
        text,
    )
    return text


# ---------------------------------------------------------------------------
# digits to characters
# ---------------------------------------------------------------------------
_ONES = ["صفر", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
_TEENS = ["ده", "یازده", "دوازده", "سیزده", "چهارده", "پانزده",
          "شانزده", "هفده", "هجده", "نوزده"]
_TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
_HUNDREDS = ["", "صد", "دویست", "سیصد", "چهارصد", "پانصد",
             "ششصد", "هفتصد", "هشتصد", "نهصد"]
_SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون", "کوادریلیون"]


def digits_to_words(digits: str) -> str:
    """ 
    It reads digit by digit: '0912' -> zero nine one two
    """

    return " ".join(_ONES[int(c)] for c in digits if c.isdigit())


def _triplet_words(n: int) -> list[str]:
    parts: list[str] = []
    h, r = divmod(n, 100)
    if h:
        parts.append(_HUNDREDS[h])
    if 10 <= r < 20:
        parts.append(_TEENS[r - 10])
    else:
        t, o = divmod(r, 10)
        if t >= 2:
            parts.append(_TENS[t])
        if o:
            parts.append(_ONES[o])
    return parts


def number_to_words(n: int) -> str:
    """convert number to word"""
    if n < 0:
        return "منفی " + number_to_words(-n)
    if n == 0:
        return _ONES[0]
    if n >= 10 ** (3 * len(_SCALES)):       
        return digits_to_words(str(n))
    groups: list[int] = []
    while n:
        n, g = divmod(n, 1000)
        groups.append(g)
    parts: list[str] = []
    for idx in reversed(range(len(groups))):
        g = groups[idx]
        if not g:
            continue
        words = " و ".join(_triplet_words(g))
        if idx == 1 and g == 1:
            words = "هزار"                 
        elif idx:
            words += " " + _SCALES[idx]
        parts.append(words)
    return " و ".join(parts)


def number_to_ordinal(n: int) -> str:
    """convert number to ordinal"""
    if n == 1:
        return "اول"
    w = number_to_words(n)
    if w.endswith("سه"):
        return w[:-2] + "سوم"
    if w.endswith("ی"):                      # سی
        return w + ZWNJ + "ام"
    return w + "م"


_FRAC_PLACES = {
    1: "دهم", 2: "صدم", 3: "هزارم",
    4: f"ده{ZWNJ}هزارم", 5: f"صد{ZWNJ}هزارم", 6: "میلیونیم",
}


def decimal_to_words(int_part: str, frac_part: str) -> str:
    ip = number_to_words(int(int_part))
    frac_val = int(frac_part)
    place = _FRAC_PLACES.get(len(frac_part))
    if frac_val > 0 and place:
        return f"{ip} ممیز {number_to_words(frac_val)} {place}"
    return f"{ip} ممیز {digits_to_words(frac_part)}"


# ---------------------------------------------------------------------------
# Date, time, phone
# ---------------------------------------------------------------------------
_JALALI_MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
                  "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
_GREGORIAN_MONTHS = ["ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
                     "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"]

_DATE_RE = re.compile(r"(?<![\d/-])(\d{4})([/-])(\d{1,2})\2(\d{1,2})(?![\d/-])")


def expand_dates(text: str) -> str:
    """ 
    year < 1700 = 'Gregorian date'  else  'jalali date'
    and convert date to word
    """
    def repl(m: re.Match) -> str:
        y, mo, d = int(m.group(1)), int(m.group(3)), int(m.group(4))
        if not (1 <= mo <= 12 and 1 <= d <= 31):
            return m.group()
        months = _JALALI_MONTHS if y < 1700 else _GREGORIAN_MONTHS
        return f"{number_to_ordinal(d)} {months[mo - 1]} {number_to_words(y)}"
    return _DATE_RE.sub(repl, text)


_TIME_RE = re.compile(r"(?<![\d:])([01]?\d|2[0-3]):([0-5]\d)(?![\d:])")


def expand_times(text: str) -> str:
    """14:30 -> چهارده و سی دقیقه"""
    def repl(m: re.Match) -> str:
        h, mi = int(m.group(1)), int(m.group(2))
        out = number_to_words(h)
        if mi:
            out += f" و {number_to_words(mi)} دقیقه"
        return out
    return _TIME_RE.sub(repl, text)


_MOBILE_RE = re.compile(r"(?<!\d)(09\d{2})[-\s]?(\d{3})[-\s]?(\d{4})(?!\d)")
_LANDLINE_RE = re.compile(
    r"(?<!\d)(0\d{2,3})[-\s]?(\d{7,8})(?!\d)"
)


def expand_phone_numbers(text: str) -> str:
    """ 
    "It reads mobile/landline numbers group by group and digit by digit.
    """
    def join(*groups: str) -> str:
        return "، ".join(digits_to_words(g) for g in groups)
    text = _MOBILE_RE.sub(lambda m: join(*m.groups()), text)
    text = _LANDLINE_RE.sub(lambda m: join(*m.groups()), text)
    return text


# ---------------------------------------------------------------------------
# Symbols and units
# ---------------------------------------------------------------------------
_UNITS = {
    "km/h": "کیلومتر بر ساعت", "km": "کیلومتر", "cm": "سانتی‌متر",
    "mm": "میلی‌متر", "m": "متر", "kg": "کیلوگرم", "mg": "میلی‌گرم",
    "g": "گرم", "ml": "میلی‌لیتر", "L": "لیتر",
    "KB": "کیلوبایت", "MB": "مگابایت", "GB": "گیگابایت", "TB": "ترابایت",
    "Hz": "هرتز", "kHz": "کیلوهرتز", "MHz": "مگاهرتز", "GHz": "گیگاهرتز",
}
_UNITS_RE = re.compile(
    r"(?<=\d)\s?("
    + "|".join(re.escape(u) for u in sorted(_UNITS, key=len, reverse=True))
    + r")(?![A-Za-z/²³])"
)
_CURRENCY = {"$": "دلار", "€": "یورو", "£": "پوند"}
_CURRENCY_RE = re.compile(r"([$€£])\s?(\d+(?:\.\d+)?)")


def expand_symbols_and_units(text: str) -> str:
    """45% -> 45 درصد ، 25°C -> 25 درجه سانتی‌گراد ، 5km -> 5 کیلومتر ، $50 -> 50 دلار"""
    text = _CURRENCY_RE.sub(lambda m: f"{m.group(2)} {_CURRENCY[m.group(1)]}", text)
    text = re.sub(r"\s*(?:°\s?C|℃)", " درجه سانتی‌گراد", text)
    text = re.sub(r"\s*(?:°\s?F|℉)", " درجه فارنهایت", text)
    text = re.sub(r"\s*°", " درجه", text)
    text = re.sub(r"\s*[%٪]", " درصد", text)
    text = _UNITS_RE.sub(lambda m: " " + _UNITS[m.group(1)], text)
    return text


# ---------------------------------------------------------------------------
# تبدیل اعداد باقی‌مانده
# ---------------------------------------------------------------------------
_ORDINAL_RE = re.compile(
    rf"(?<![\d.])(\d+){ZWNJ}?(مین|ام|م)(?![\u0600-\u06FF])"
)


def expand_ordinals(text: str) -> str:
    """3ام -> سوم ، 5م -> پنجم ، 2مین -> دومین"""
    def repl(m: re.Match) -> str:
        word = number_to_ordinal(int(m.group(1)))
        return word + "ین" if m.group(2) == "مین" else word
    return _ORDINAL_RE.sub(repl, text)


def expand_negatives_and_ranges(text: str) -> str:
    """-5 -> منفی 5 ؛ 10-20 -> 10 تا 20"""
    text = re.sub(r"(?<!\w)[-−](?=\d)", "منفی ", text)
    text = re.sub(r"(?<=\d)\s?[-–]\s?(?=\d)", " تا ", text)
    return text


_DECIMAL_RE = re.compile(r"(?<![\d.])(\d+)\.(\d+)(?!\d|\.\d)")


def expand_decimals(text: str) -> str:
    """3.14 -> سه ممیز چهارده صدم"""
    return _DECIMAL_RE.sub(lambda m: decimal_to_words(m.group(1), m.group(2)), text)


def expand_integers(text: str) -> str:
    """هر عدد صحیح باقی‌مانده. اعداد با صفر اول (مثل 007) رقم‌به‌رقم خوانده می‌شوند."""
    def repl(m: re.Match) -> str:
        s = m.group()
        if (len(s) > 1 and s[0] == "0") or len(s) > 18:
            return digits_to_words(s)
        return number_to_words(int(s))
    return re.sub(r"\d+", repl, text)


def convert_numbers(text: str) -> str:
    """ 
    All the steps of converting numbers to words
    """
    text = normalize_digits(text)
    text = expand_dates(text)
    text = expand_times(text)
    text = expand_phone_numbers(text)
    text = expand_symbols_and_units(text)
    text = expand_negatives_and_ranges(text)
    text = expand_ordinals(text)
    text = expand_decimals(text)
    text = expand_integers(text)
    return text


# ---------------------------------------------------------------------------
# کلمات لاتین و علائم نگارشی
# ---------------------------------------------------------------------------
LATIN_WORDS = {
    "AI": "ای آی", "API": "ای پی آی", "CPU": "سی پی یو", "GPU": "جی پی یو",
    "TTS": "تی تی اس", "USB": "یو اس بی", "PDF": "پی دی اف",
    "Wi-Fi": f"وای{ZWNJ}فای", "WiFi": f"وای{ZWNJ}فای","Python": "پایتون",
    "Linux": "لینوکس","Hugging Face": "هاگینگ فیس",
}


def replace_latin_words(text: str, mapping: dict[str, str] | None = None) -> str:
    """کلمات/اختصارات لاتین را با تلفظ فارسی جایگزین می‌کند (حساس به حروف بزرگ و کوچک).
    دیکشنری را خودت گسترش بده.
    """
    mapping = LATIN_WORDS if mapping is None else mapping
    for key in sorted(mapping, key=len, reverse=True):
        text = re.sub(
            rf"(?<![A-Za-z]){re.escape(key)}(?![A-Za-z])", mapping[key], text
        )
    return text


def normalize_punctuation(text: str) -> str:
    """؟ ، ؛ فارسی بعد از حرف فارسی؛ حذف گیومه و نقل‌قول؛ تکرار علائم."""
    text = re.sub(r"(?<=[\u0600-\u06FF])\s?\?", "؟", text)
    text = re.sub(r"(?<=[\u0600-\u06FF]),", "،", text)
    text = re.sub(r"(?<=[\u0600-\u06FF]);", "؛", text)
    text = text.replace("…", "...")
    text = re.sub(r"[«»“”\"]", "", text)
    text = re.sub(r"([!؟?])\1+", r"\1", text)
    return text


# ---------------------------------------------------------------------------
# pipeline(main function)
# ---------------------------------------------------------------------------
def preprocess(
    text: str,
    *,
    latin_words: dict[str, str] | None = None,
    strip_diacritics: bool = True,
) -> str:
    """کل پیش‌پردازش روی یک متن؛ خروجی هنوز یک رشته است."""
    text = normalize_chars(text, strip_diacritics=strip_diacritics)
    text = normalize_whitespace(text)
    text = convert_numbers(text)
    text = replace_latin_words(text, latin_words)
    text = normalize_punctuation(text)
    return normalize_whitespace(text)
