"""JSON-configured monitor runner for desktop shells."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .config import Settings
from .members import Member
from .monitor import AuctionMonitor


def _settings_from_payload(payload: dict) -> Settings:
    return Settings(
        api_key=payload.get("api_key", ""),
        video_id=payload.get("video_id", ""),
        member_file=payload.get("member_file") or "회원명단.xlsx",
        blocked_file=payload.get("blocked_file") or "차단목록.xlsx",
        col_id=payload.get("col_id", "아이디"),
        col_name=payload.get("col_name", "고객명"),
        col_phone=payload.get("col_phone", "연락처"),
        col_address=payload.get("col_address", "주소"),
        host_keyword=payload.get("host_keyword", "만물도깨비"),
        poll_sec=max(int(payload.get("poll_sec", 6)), 6),
        sort_by_name=bool(payload.get("sort_by_name", True)),
        output_dir=payload.get("output_dir") or ".",
    )


def _members_from_payload(payload: dict) -> dict[str, Member]:
    members: dict[str, Member] = {}
    for row in payload.get("extra_members", []):
        key = str(row.get("key", "")).strip()
        if not key:
            continue
        members[key] = Member(
            customer_name=str(row.get("customer_name", "")).strip(),
            phone=str(row.get("phone", "")).strip(),
            address=str(row.get("address", "")).strip(),
        )
    return members


def main() -> None:
    if len(sys.argv) != 2:
        print("사용법: python3 -m auction.run_monitor config.json", file=sys.stderr)
        sys.exit(2)

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    monitor = AuctionMonitor(
        _settings_from_payload(payload),
        extra_members=_members_from_payload(payload),
        log=lambda message: print(message, flush=True),
    )
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("중지 요청", flush=True)


if __name__ == "__main__":
    main()
