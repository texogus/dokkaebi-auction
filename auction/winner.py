"""Winner determination for bidding and first-come auctions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bid:
    time_text: str
    uid: str
    display_name: str
    value: float | int
    published_at: str = ""
    sequence: int = 0


@dataclass(frozen=True)
class Winner:
    uid: str
    display_name: str
    value: float | int
    time_text: str


def _is_extreme_high_outlier(highest: float | int, next_highest: float | int, participant_count: int) -> bool:
    if participant_count < 3:
        return False
    return highest > next_highest * 5 and highest - next_highest >= 50


def _bid_order_key(bid: Bid, fallback_index: int) -> tuple[str, int]:
    published_at = bid.published_at or f"~{fallback_index:010d}"
    return published_at, bid.sequence or fallback_index


def determine_winners(bids: list[Bid], auction_type: str, limit: int) -> list[Winner]:
    """Determine winners from bids before the winning line."""
    if not bids:
        return []

    if auction_type == "first_come":
        seen: set[str] = set()
        winners: list[Winner] = []
        filled = 0
        ordered_bids = sorted(enumerate(bids), key=lambda item: _bid_order_key(item[1], item[0]))
        for _, bid in ordered_bids:
            if bid.uid in seen:
                continue
            seen.add(bid.uid)
            remaining = limit - filled
            if remaining <= 0:
                break
            quantity = min(int(bid.value), remaining)
            winners.append(Winner(bid.uid, bid.display_name, quantity, bid.time_text))
            filled += quantity
            if filled >= limit:
                break
        return winners

    best: dict[str, float | int] = {}
    meta: dict[str, tuple[str, str, tuple[str, int]]] = {}
    for index, bid in enumerate(bids):
        if bid.uid not in best or bid.value > best[bid.uid]:
            best[bid.uid] = bid.value
            meta[bid.uid] = (bid.display_name, bid.time_text, _bid_order_key(bid, index))

    ranked = sorted(best.items(), key=lambda item: (-item[1], meta[item[0]][2]))
    if len(ranked) >= 3:
        highest_uid, highest_value = ranked[0]
        next_value = ranked[1][1]
        if _is_extreme_high_outlier(highest_value, next_value, len(ranked)):
            ranked = [item for item in ranked if item[0] != highest_uid]

    return [
        Winner(uid=uid, display_name=meta[uid][0], value=value, time_text=meta[uid][1])
        for uid, value in ranked[:limit]
    ]
