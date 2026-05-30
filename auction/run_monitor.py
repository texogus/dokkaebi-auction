"""JSON-configured monitor runner for desktop shells."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from googleapiclient.errors import HttpError

from .config import Settings
from .members import Member
from .monitor import AuctionMonitor

MIN_POLL_SEC = 15


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
        poll_sec=max(int(payload.get("poll_sec", MIN_POLL_SEC)), MIN_POLL_SEC),
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
    except HttpError as exc:
        if exc.resp.status == 403 and "quotaExceeded" in str(exc):
            print(
                "YouTube API 일일 사용량을 초과했습니다.\n"
                "오늘 사용한 API 키는 더 이상 요청할 수 없습니다.\n"
                "해결 방법: Google Cloud Console에서 YouTube Data API 할당량이 회복될 때까지 기다리거나, "
                "새 API 키를 입력한 뒤 다시 시작하세요.\n"
                "앱은 API 소모를 줄이기 위해 폴링 간격을 최소 15초로 제한합니다.",
                flush=True,
            )
            sys.exit(3)
        raise


if __name__ == "__main__":
    main()
