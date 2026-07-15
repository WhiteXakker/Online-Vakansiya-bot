import re


def validate_age(value: str) -> tuple[bool, str]:
    value = value.strip()
    if not value.isdigit():
        return False, "Yosh raqam bo'lishi kerak. Qayta kiriting:"
    age = int(value)
    if age < 10 or age > 100:
        return False, "Yosh 10 dan 100 gacha bo'lishi kerak. Qayta kiriting:"
    return True, ""


def validate_phone(value: str) -> tuple[bool, str]:
    value = value.strip().replace(" ", "").replace("-", "")
    if re.fullmatch(r"\+?\d{9,15}", value):
        return True, ""
    return False, "Telefon raqam noto'g'ri. Qayta kiriting (masalan: +998901234567):"


def validate_telegram(value: str) -> tuple[bool, str]:
    value = value.strip()
    if value.startswith("@"):
        value = value[1:]
    if re.fullmatch(r"[a-zA-Z0-9_]{5,32}", value):
        return True, ""
    if value.isdigit() or value.startswith("+"):
        return True, ""
    return False, "Telegram username noto'g'ri. @username yoki raqam kiriting:"


def validate_non_empty(value: str, min_len: int = 2) -> tuple[bool, str]:
    if len(value.strip()) >= min_len:
        return True, ""
    return False, f"Kamida {min_len} ta belgi kiriting. Qayta urinib ko'ring:"
