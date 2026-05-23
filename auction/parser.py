"""Chat message parsing for bids and quantities."""

from __future__ import annotations

import re


_BID_RE = re.compile(r"^[\d.,\s]+$")
_NOISE_RE = re.compile(r"[가-힣ㄱ-ㅎㅏ-ㅣa-zA-Z]")


def is_bid_message(text: str) -> bool:
    """Return true when a chat message contains only numeric bid-like text."""
    stripped = text.strip()
    if not stripped:
        return False
    if _NOISE_RE.search(stripped):
        return False
    return bool(_BID_RE.match(stripped))


def parse_number(text: str) -> float | None:
    """Parse auction bid text into a numeric value.

    Accepts common decimal variants such as ",5", "..5", "0,5", ",,5",
    "0,,5", and "0..5" as 0.5.
    """
    stripped = text.strip()
    stripped = re.sub(r"^[.,]+", "0.", stripped)
    stripped = stripped.replace(",", ".")
    stripped = re.sub(r"[^\d.]", "", stripped)
    if not stripped:
        return None
    if stripped.count(".") > 1:
        parts = stripped.split(".")
        stripped = parts[0] + "." + "".join(parts[1:])
    try:
        value = float(stripped)
        return value if value > 0 else None
    except ValueError:
        return None


def parse_qty(text: str) -> int | None:
    """Parse first-come quantity text. Only positive integers are valid."""
    stripped = text.strip()
    if not re.match(r"^\d+$", stripped):
        return None
    quantity = int(stripped)
    return quantity if quantity >= 1 else None
