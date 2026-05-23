"""Runtime configuration for the auction automation."""

from dataclasses import dataclass
import os
from datetime import timezone, timedelta


KST = timezone(timedelta(hours=9))


@dataclass(frozen=True)
class Settings:
    api_key: str
    video_id: str
    member_file: str
    blocked_file: str
    col_id: str
    col_name: str
    col_phone: str
    col_address: str
    host_keyword: str
    poll_sec: int
    sort_by_name: bool
    output_dir: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            api_key=os.getenv("YOUTUBE_API_KEY", "YOUR_YOUTUBE_API_KEY"),
            video_id=os.getenv("YOUTUBE_VIDEO_ID", "qxv6hXXFdXA"),
            member_file=os.getenv("MEMBER_FILE", "회원명단.xlsx"),
            blocked_file=os.getenv("BLOCKED_FILE", "차단목록.xlsx"),
            col_id=os.getenv("COL_ID", "아이디"),
            col_name=os.getenv("COL_NAME", "고객명"),
            col_phone=os.getenv("COL_PHONE", "연락처"),
            col_address=os.getenv("COL_ADDRESS", "주소"),
            host_keyword=os.getenv("HOST_KEYWORD", "만물도깨비"),
            poll_sec=int(os.getenv("POLL_SEC", "6")),
            sort_by_name=os.getenv("SORT_BY_NAME", "true").lower() in {"1", "true", "yes", "y"},
            output_dir=os.getenv("OUTPUT_DIR", "."),
        )
