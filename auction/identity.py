"""Identity normalization helpers."""


def normalize_id(raw: str) -> str:
    """Normalize YouTube display names for member and block-list matching."""
    return str(raw).strip().lower().lstrip("@")
