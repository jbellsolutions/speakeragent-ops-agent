from __future__ import annotations

import argparse
import asyncio

from .config import load_settings
from .reports import build_daily_markdown
from .runner import run_daily, run_uptime


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run SpeakerAgent ops checks once.")
    parser.add_argument("command", choices=["uptime", "daily"])
    args = parser.parse_args()

    settings = load_settings()
    report = await (run_daily(settings) if args.command == "daily" else run_uptime(settings))
    print(build_daily_markdown(report) if args.command == "daily" else report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

