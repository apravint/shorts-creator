"""Keyword matching shared by the script and visual engines."""

import re
from typing import Iterable


def has_term(text: str, terms: Iterable[str]) -> bool:
    """
    True if any term occurs in text.
    Latin terms match whole words only, so "ai" does not match "rain" and "war" does not match "toward".
    Tamil terms match as substrings because Tamil words carry their suffixes attached.
    """
    lowered = (text or "").lower()
    for term in terms:
        if term.isascii():
            if re.search(rf"\b{re.escape(term)}\b", lowered):
                return True
        elif term in lowered:
            return True
    return False
