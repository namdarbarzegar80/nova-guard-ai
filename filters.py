import re


URL_PATTERN = re.compile(
    r"(https?://|www\.|t\.me/|telegram\.me/)",
    re.IGNORECASE
)


def has_link(text: str) -> bool:
    if not text:
        return False

    return bool(URL_PATTERN.search(text))


def contains_bad_word(
    text: str,
    words: list[str]
) -> bool:

    if not text:
        return False

    text = text.lower()

    for word in words:

        word = word.strip().lower()

        if not word:
            continue

        if word in text:
            return True

    return False
