"""Identity normalization helpers."""


def normalize_id(raw: str) -> str:
    """Normalize YouTube display names for member and block-list matching."""
    return str(raw).strip().lower().lstrip("@")


def display_id(raw: str) -> str:
    """Return the display name used in order sheets without a leading @."""
    return str(raw).strip().lstrip("@")
