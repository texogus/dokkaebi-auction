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
    limit_match = re.search(r"\[(\d+)개한정\]", host_message)
    auction_type = "first_come" if limit_match else "bidding"
    limit = int(limit_match.group(1)) if limit_match else 1

    price = 0
    ten_thousand = re.search(r"(\d[\d,]*)\s*만\s*원", host_message)
    thousand = re.search(r"(\d[\d,]*)\s*천\s*원", host_message)
    won = re.search(r"(\d[\d,]+)\s*원", host_message)
    if ten_thousand:
        price = int(ten_thousand.group(1).replace(",", "")) * 10000
    elif thousand:
        price = int(thousand.group(1).replace(",", "")) * 1000
    elif won:
        price = int(won.group(1).replace(",", ""))

    return AuctionDetails(auction_type=auction_type, limit=limit, base_price=price)


def is_auction_start(text: str) -> bool:
    return any(keyword in text for keyword in ["출발", "한정", "경매", "★", "☆"])


def is_winning_line(text: str) -> bool:
    return "낙찰선" in text or ("낙찰" in text and "선" in text)
