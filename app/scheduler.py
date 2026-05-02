from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import Settings
from .models import RunReport
from .runner import run_daily, run_uptime


class OpsScheduler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.tasks: list[asyncio.Task[None]] = []
        self.last_report: RunReport | None = None
        self._lock = asyncio.Lock()

    def start(self) -> None:
        if self.tasks:
            return
        self.tasks.append(asyncio.create_task(self._uptime_loop()))
        self.tasks.append(asyncio.create_task(self._daily_loop()))

    async def stop(self) -> None:
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks.clear()

    async def run_uptime_now(self) -> RunReport:
        async with self._lock:
            self.last_report = await run_uptime(self.settings)
            return self.last_report

    async def run_daily_now(self) -> RunReport:
        async with self._lock:
            self.last_report = await run_daily(self.settings)
            return self.last_report

    async def _uptime_loop(self) -> None:
        while True:
            try:
                await self.run_uptime_now()
            except Exception as exc:
                print(f"[scheduler] uptime run failed: {exc}", flush=True)
            await asyncio.sleep(max(self.settings.uptime_interval_seconds, 60))

    async def _daily_loop(self) -> None:
        while True:
            await asyncio.sleep(seconds_until_next_daily(self.settings.daily_report_hour_eastern))
            try:
                await self.run_daily_now()
            except Exception as exc:
                print(f"[scheduler] daily run failed: {exc}", flush=True)


def seconds_until_next_daily(hour: int) -> float:
    eastern = ZoneInfo("America/New_York")
    now = datetime.now(eastern)
    target = now.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= now:
        target += timedelta(days=1)
    return (target - now).total_seconds()

