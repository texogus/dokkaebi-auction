"""PyInstaller entry point for bundled desktop helper commands."""

import sys

from auction.member_writer import main as member_writer_main
from auction.run_monitor import main


if __name__ == "__main__":
    if len(sys.argv) >= 2 and sys.argv[1] == "append-member":
        sys.argv = [sys.argv[0], *sys.argv[2:]]
        member_writer_main()
    else:
        main()
