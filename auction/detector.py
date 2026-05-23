"""Auction start, type, price, and close-line detection."""

from __future__ import annotations

from dataclasses import dataclass
import re


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
    limit_match = re.search(r"[\[(]\s*(\d+)\s*개\s*한정\s*[\])]", host_message)
    auction_type = "bidding" if re.match(r"^경매\s*>", stripped) else "first_come"
    limit = int(limit_match.group(1)) if limit_match else 1

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


def is_auction_start(text: str) -> bool:
    stripped = text.strip()
    is_bidding_start = bool(re.match(r"^경매\s*>", stripped) and "출발" in stripped)
    is_limited_start = bool(
        re.search(r"[\[(]\s*\d+\s*개\s*한정\s*[\])]", stripped)
        and _has_price(stripped)
        and "@" not in stripped
    )
    return is_bidding_start or is_limited_start


def is_winning_line(text: str) -> bool:
    return "낙찰선" in text or ("낙찰" in text and "선" in text)


def is_no_sale_line(text: str) -> bool:
    return "유찰" in text
