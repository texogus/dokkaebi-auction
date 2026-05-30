"""Reusable live auction monitor engine."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Callable

from googleapiclient.errors import HttpError

from .config import Settings
from .detector import detect_auction, detect_bid_increment, is_auction_start, is_no_sale_line, is_winning_line
from .identity import display_id, normalize_id
from .members import Member, load_blocked, load_members
from .parser import is_bid_message, parse_number, parse_qty
from .winner import Bid, determine_winners
from .workbook import OrderRow, init_workbook, sort_and_renumber, write_order_row
from .youtube_client import build_youtube, fetch_messages, get_live_chat_id, parse_kst


LogCallback = Callable[[str], None]


@dataclass(frozen=True)
class MonitorResult:
    output_file: str
    order_count: int
    participant_count: int


def _price_and_quantity(auction_type: str, winner_value: float | int, base_price: int) -> tuple[int, int]:
    if auction_type == "first_come":
        return base_price, int(winner_value)
    price = int(winner_value * 10000)
    return price, 1


def _normalize_bid_value(raw_value: float | int, base_price: int) -> float | int:
    """Normalize compact bids such as 65 as 6.5 for sub-100,000 won starts."""
    base_manwon = base_price / 10000
    compact_value = raw_value / 10
    if 5 <= base_manwon < 10 and 10 <= raw_value < 100 and compact_value >= base_manwon:
        return compact_value
    return raw_value


def _is_valid_bid_increment(value: float | int, increment: float | None) -> bool:
    if increment is None or increment <= 0:
        return True
    quotient = float(value) / increment
    return abs(quotient - round(quotient)) < 0.000001


def _message_sort_key(item: dict) -> str:
    return str(item.get("snippet", {}).get("publishedAt", ""))


def _poll_wait_seconds(polling_interval_millis: int | float, configured_poll_sec: int, in_auction: bool) -> float:
    api_wait = max(float(polling_interval_millis) / 1000, 1)
    if in_auction:
        return api_wait
    return max(api_wait, configured_poll_sec)


def _removed_message_id(snippet: dict) -> str | None:
    message_type = snippet.get("type")
    if message_type == "messageDeletedEvent":
        return snippet.get("messageDeletedDetails", {}).get("deletedMessageId")
    if message_type == "messageRetractedEvent":
        return snippet.get("messageRetractedDetails", {}).get("retractedMessageId")
    return None


def _tags(is_member: bool, is_blocked: bool, duplicate_count: int) -> list[str]:
    tags: list[str] = []
    if not is_member:
        tags.append("미가입")
    if is_blocked:
        tags.append("차단")
    if duplicate_count > 1:
        tags.append(f"중복{duplicate_count}회")
    return tags


class AuctionMonitor:
    """Run YouTube live auction monitoring until stopped."""

    def __init__(
        self,
        settings: Settings,
        *,
        extra_members: dict[str, Member] | None = None,
        stop_event: Event | None = None,
        log: LogCallback | None = None,
    ) -> None:
        self.settings = settings
        self.extra_members = extra_members or {}
        self.stop_event = stop_event or Event()
        self.log = log or print

    def run(self) -> MonitorResult:
        if self.settings.api_key == "YOUR_YOUTUBE_API_KEY":
            raise RuntimeError("YouTube API 키를 입력하세요.")

        members = load_members(self.settings)
        members.update(self.extra_members)
        blocked = load_blocked(self.settings)
        youtube = build_youtube(self.settings)
        chat_id = get_live_chat_id(youtube, self.settings.video_id)

        output_dir = Path(self.settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = str(output_dir / f"주문서_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx")
        workbook, sheet = init_workbook()

        in_auction = False
        product_name = ""
        auction_type = "bidding"
        auction_limit = 1
        base_price = 0
        bid_increment: float | None = None
        bids: list[Bid] = []

        order_sequence = 1
        order_row_number = 2
        all_orders: list[OrderRow] = []
        session_count: dict[str, int] = {}
        processed: set[str] = set()
        bid_by_message_id: dict[str, Bid] = {}
        removed_bid_message_ids: set[str] = set()
        message_sequence = 0
        page_token: str | None = None

        self.log(f"실시간 모니터링 시작\n{'-' * 55}")

        try:
            while not self.stop_event.is_set():
                try:
                    response = fetch_messages(youtube, chat_id, page_token)
                except HttpError as exc:
                    code = exc.resp.status
                    wait = 30 if code == 403 else 10
                    self.log(f"API 오류 {code}: {wait}초 후 재시도")
                    self.stop_event.wait(wait)
                    continue
                except Exception as exc:
                    wait = 5 if in_auction else 15
                    self.log(f"네트워크/API 연결 오류: {wait}초 후 재시도 ({exc})")
                    self.stop_event.wait(wait)
                    continue

                page_token = response.get("nextPageToken")
                polling_interval = response.get("pollingIntervalMillis", self.settings.poll_sec * 1000)
                items = response.get("items", [])

                for item in sorted(items, key=_message_sort_key):
                    if self.stop_event.is_set():
                        break

                    message_id = item["id"]
                    if message_id in processed:
                        continue
                    processed.add(message_id)
                    message_sequence += 1

                    snippet = item["snippet"]
                    removed_message_id = _removed_message_id(snippet)
                    if removed_message_id:
                        removed_bid_message_ids.add(removed_message_id)
                        removed_bid = bid_by_message_id.pop(removed_message_id, None)
                        if removed_bid:
                            bids = [bid for bid in bids if bid is not removed_bid]
                            self.log(f"  취소된 입찰 제외: {removed_bid.display_name}")
                        continue

                    if snippet.get("type", "textMessageEvent") != "textMessageEvent":
                        continue

                    author = item["authorDetails"]
                    text = snippet.get("displayMessage", "").strip()
                    display_name = display_id(author.get("displayName", ""))
                    uid = normalize_id(display_name)
                    time_text = parse_kst(snippet.get("publishedAt", ""))
                    published_at = str(snippet.get("publishedAt", ""))
                    is_host = (
                        author.get("isChatOwner", False)
                        or author.get("isChatModerator", False)
                        or self.settings.host_keyword in display_name
                    )

                    if is_host:
                        if is_no_sale_line(text):
                            if not in_auction:
                                continue

                            label = "선착순" if auction_type == "first_come" else "경매"
                            self.log(f"\n[{label}] 유찰: 낙찰 없이 종료")

                            in_auction = False
                            product_name = ""
                            auction_type = "bidding"
                            auction_limit = 1
                            base_price = 0
                            bid_increment = None
                            bids = []
                            bid_by_message_id = {}
                            self.log(f"{'-' * 55}")
                        elif is_winning_line(text):
                            if not in_auction:
                                continue

                            if bids:
                                winners = determine_winners(bids, auction_type, auction_limit)
                                label = "선착순" if auction_type == "first_come" else "경매"
                                self.log(f"\n[{label}] 낙찰: {len(winners)}명")

                                for winner in winners:
                                    member = members.get(winner.uid, Member())
                                    is_member = bool(member.customer_name or member.phone or member.address)
                                    is_blocked = winner.uid in blocked
                                    session_count[winner.uid] = session_count.get(winner.uid, 0) + 1
                                    duplicate_count = session_count[winner.uid]
                                    notes = " | ".join(_tags(is_member, is_blocked, duplicate_count))
                                    price, quantity = _price_and_quantity(auction_type, winner.value, base_price)

                                    order = OrderRow(
                                        time_text=winner.time_text,
                                        sequence=order_sequence,
                                        product=product_name,
                                        price=price,
                                        quantity=quantity,
                                        uid=winner.display_name,
                                        member=member,
                                        is_member=is_member,
                                        is_blocked=is_blocked,
                                        is_duplicate=duplicate_count > 1,
                                        notes=notes,
                                        auction_type=auction_type,
                                    )
                                    write_order_row(sheet, order_row_number, order)
                                    all_orders.append(order)

                                    status = "정상" if is_member and not is_blocked else ("차단" if is_blocked else "미가입")
                                    duplicate_label = f" 중복{duplicate_count}회" if duplicate_count > 1 else ""
                                    self.log(f"  {status} {winner.display_name:<22} | {price:,}원 x {quantity}{duplicate_label}")

                                    order_sequence += 1
                                    order_row_number += 1

                                workbook.save(output_file)
                                self.log(f"  저장: {output_file}")
                            else:
                                self.log("\n낙찰선 감지됐으나 입찰 없음")

                            in_auction = False
                            bids = []
                            bid_by_message_id = {}
                            bid_increment = None
                            self.log(f"{'-' * 55}")
                        elif is_auction_start(text):
                            if in_auction:
                                self.log(f"진행 중 시작 후보 무시: {text}")
                                continue
                            details = detect_auction(text)
                            in_auction = True
                            bids = []
                            bid_by_message_id = {}
                            product_name = text
                            auction_type = details.auction_type
                            auction_limit = details.limit
                            base_price = details.base_price
                            bid_increment = None
                            self.log(f"\n[{details.type_label}] 시작")
                            self.log(f"   상품: {product_name}")
                            self.log(f"   한정: {auction_limit}개 | 기준가: {base_price:,}원")
                        else:
                            detected_increment = detect_bid_increment(text)
                            if in_auction and auction_type == "bidding" and detected_increment is not None:
                                bid_increment = detected_increment
                                self.log(f"   입찰 단위: {int(detected_increment * 10000):,}원")

                    elif in_auction and is_bid_message(text):
                        if auction_type == "first_come":
                            value = parse_qty(text)
                            label = "수량"
                        else:
                            parsed_value = parse_number(text)
                            value = _normalize_bid_value(parsed_value, base_price) if parsed_value is not None else None
                            label = "입찰가"
                            if value is not None and not _is_valid_bid_increment(value, bid_increment):
                                self.log(f"  입찰 단위 불일치 제외: {display_name} -> {text.strip()!r}")
                                value = None

                        if value is not None:
                            if message_id in removed_bid_message_ids:
                                continue
                            bid = Bid(
                                time_text=time_text,
                                uid=uid,
                                display_name=display_name,
                                value=value,
                                published_at=published_at,
                                sequence=message_sequence,
                            )
                            bids.append(bid)
                            bid_by_message_id[message_id] = bid
                            self.log(f"  {display_name:<22} -> {text.strip()!r:>6} ({label}: {value})")

                if len(items) >= 190:
                    self.log(f"이전 채팅 따라잡는 중: {len(items)}개 처리")
                    continue

                self.stop_event.wait(_poll_wait_seconds(polling_interval, self.settings.poll_sec, in_auction))
        finally:
            if self.settings.sort_by_name and all_orders:
                self.log("고객명 가나다 순 정렬 중...")
                sort_and_renumber(sheet, all_orders)

            workbook.save(output_file)
            self.log(f"\n최종 저장 완료: {output_file}")
            self.log(f"총 처리 주문: {order_sequence - 1}건")
            self.log(f"총 참여 회원: {len(session_count)}명")

        return MonitorResult(
            output_file=output_file,
            order_count=order_sequence - 1,
            participant_count=len(session_count),
        )
