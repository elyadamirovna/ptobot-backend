"""Phone normalization helpers for auth flows."""
from __future__ import annotations


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())

    if len(digits) == 11 and digits.startswith("8"):
        return "7" + digits[1:]
    if len(digits) == 10:
        return "7" + digits
    return digits
