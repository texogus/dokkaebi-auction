"""Winner determination for bidding and first-come auctions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Bid:
    time_text: str
    uid: str
    display_name: str
    value: float | int


@dataclass(frozen=True)
class Winner:
    uid: str
    display_name: str
    value: float | int
    time_text: str


def determine_winners(bids: list[Bid], auction_type: str, limit: int) -> list[Winner]:
    """Determine winners from bids before the winning line."""
    if not bids:
        return []

    if auction_type == "first_come":
        seen: set[str] = set()
        winners: list[Winner] = []
        filled = 0
        for bid in bids:
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
    meta: dict[str, tuple[str, str]] = {}
    for bid in bids:
        if bid.uid not in best or bid.value > best[bid.uid]:
            best[bid.uid] = bid.value
            meta[bid.uid] = (bid.display_name, bid.time_text)

    ranked = sorted(best.items(), key=lambda item: -item[1])
    return [
        Winner(uid=uid, display_name=meta[uid][0], value=value, time_text=meta[uid][1])
        for uid, value in ranked[:limit]
    ]
