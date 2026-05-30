"""Auction start, type, price, and close-line detection."""

from __future__ import annotations

from dataclasses import dataclass
import re


_BIDDING_MARKER_RE = re.compile(r"<?\s*경매\s*>")
_CLOSE_MARKER_RE = re.compile(r"낙찰|유찰")
_LIMIT_MARKER_RE = re.compile(r"[\[(<]\s*(\d[\d,]*)\s*[^)\]>]*한정\s*[\])>]")
UNLIMITED_SALE_LIMIT = 1_000_000


@dataclass(frozen=True)
class AuctionDetails:
    auction_type: str
    limit: int
    base_price: int

    @property
    def type_label(self) -> str:
        return "선착순" if self.auction_type == "first_come" else "경매"


def detect_auction(host_message: str) -> AuctionDetails:
    """Detect auction type, quantity limit, and base price from host text."""
    stripped = host_message.strip()
    limit_match = _LIMIT_MARKER_RE.search(host_message)
    auction_type = "bidding" if _BIDDING_MARKER_RE.search(stripped) else "first_come"
    if auction_type == "bidding":
        limit = 1
    elif limit_match:
        limit = int(limit_match.group(1).replace(",", ""))
    else:
        limit = UNLIMITED_SALE_LIMIT

    price = 0
    ten_thousand = re.search(r"(\d[\d,]*)\s*만\s*(?:원)?", host_message)
    thousand = re.search(r"(\d[\d,]*)\s*천\s*(?:원)?", host_message)
    won = re.search(r"(\d[\d,]+)\s*원", host_message)
    if ten_thousand:
        price = int(ten_thousand.group(1).replace(",", "")) * 10000
    elif thousand:
        price = int(thousand.group(1).replace(",", "")) * 1000
    elif won:
        price = int(won.group(1).replace(",", ""))

    return AuctionDetails(auction_type=auction_type, limit=limit, base_price=price)


def _has_price(text: str) -> bool:
    return detect_auction(text).base_price > 0


def detect_bid_increment(text: str) -> float | None:
    normalized = re.sub(r"\s+", "", text)
    if "단위" not in normalized or "입찰" not in normalized:
        return None

    ten_thousand = re.search(r"(\d[\d,]*(?:\.\d+)?)만원단위입찰", normalized)
    if ten_thousand:
        return float(ten_thousand.group(1).replace(",", ""))

    thousand = re.search(r"(\d[\d,]*(?:\.\d+)?)천원단위입찰", normalized)
    if thousand:
        return float(thousand.group(1).replace(",", "")) / 10

    won = re.search(r"(\d[\d,]*)원단위입찰", normalized)
    if won:
        return int(won.group(1).replace(",", "")) / 10000

    return None


def is_auction_start(text: str) -> bool:
    stripped = text.strip()
    if _CLOSE_MARKER_RE.search(stripped) or "@" in stripped:
        return False

    is_bidding_start = bool(_BIDDING_MARKER_RE.search(stripped) and "출발" in stripped and _has_price(stripped))
    is_limited_start = bool(
        _LIMIT_MARKER_RE.search(stripped)
        and _has_price(stripped)
    )
    is_general_sale_start = bool(
        "/" in stripped
        and _has_price(stripped)
        and not _BIDDING_MARKER_RE.search(stripped)
    )
    return is_bidding_start or is_limited_start or is_general_sale_start


def is_winning_line(text: str) -> bool:
    return "낙찰선" in text or ("낙찰" in text and "선" in text)


def is_no_sale_line(text: str) -> bool:
    return "유찰" in text
