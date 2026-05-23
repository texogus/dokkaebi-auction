"""Command-line application entry point."""

from __future__ import annotations

import sys

from .config import Settings
from .monitor import AuctionMonitor


def _banner() -> None:
    print("\n만물도깨비 유튜브 경매 자동화 시스템 v1.1\n")


def main() -> None:
    _banner()
    settings = Settings.from_env()

    try:
        AuctionMonitor(settings).run()
    except RuntimeError as exc:
        print(f"오류: {exc}")
        sys.exit(1)
