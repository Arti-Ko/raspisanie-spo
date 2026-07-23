def capitalize_first(text: str) -> str:
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:]


def capitalize_full_name(text: str) -> str:
    return " ".join(capitalize_first(part) for part in text.strip().split())


def abbreviate_name(full_name: str) -> str:
    parts = full_name.split()
    if len(parts) < 2:
        return full_name
    surname, *rest = parts
    initials = ".".join(part[0].upper() for part in rest)
    return f"{surname} {initials}"
