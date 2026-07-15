import re


def clean_hashtag(value: str) -> str:
    cleaned = re.sub(r"[^\w]", "", value.lower(), flags=re.UNICODE)
    return cleaned


def generate_tech_tags(technologies: str) -> str:
    parts = re.split(r"[,;\s]+", technologies.strip())
    tags = []
    for part in parts:
        tag = clean_hashtag(part)
        if tag and f"#{tag}" not in tags:
            tags.append(f"#{tag}")
    return " ".join(tags)


def generate_region_tag(region: str) -> str:
    tag = clean_hashtag(region)
    return f"#{tag}" if tag else ""


def format_telegram_contact(value: str) -> str:
    value = value.strip()
    if value.startswith("@"):
        return value
    if value.startswith("http"):
        return value
    if value.isdigit() or value.startswith("+"):
        return value
    return f"@{value.lstrip('@')}"
