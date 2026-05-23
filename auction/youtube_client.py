"""YouTube Data API access wrappers."""

from __future__ import annotations

from datetime import datetime

from googleapiclient.discovery import build

from .config import KST, Settings


def build_youtube(settings: Settings):
    return build("youtube", "v3", developerKey=settings.api_key)


def get_live_chat_id(youtube, video_id: str) -> str:
    response = youtube.videos().list(part="liveStreamingDetails,snippet", id=video_id).execute()
    items = response.get("items", [])
    if not items:
        raise RuntimeError(f"영상을 찾을 수 없습니다: {video_id}")

    title = items[0]["snippet"]["title"]
    details = items[0].get("liveStreamingDetails", {})
    chat_id = details.get("activeLiveChatId")
    if not chat_id:
        raise RuntimeError("현재 활성화된 라이브 채팅이 없습니다. 방송 시작 후 실행하세요.")

    print(f"방송 제목: {title}")
    return chat_id


def fetch_messages(youtube, chat_id: str, page_token: str | None = None) -> dict:
    kwargs = {
        "liveChatId": chat_id,
        "part": "snippet,authorDetails",
        "maxResults": 200,
    }
    if page_token:
        kwargs["pageToken"] = page_token
    return youtube.liveChatMessages().list(**kwargs).execute()


def parse_kst(published_at: str) -> str:
    """Convert a YouTube UTC ISO timestamp into a KST 12-hour time string."""
    try:
        date_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        return date_time.astimezone(KST).strftime("%I:%M %p")
    except Exception:
        return ""
