from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CheckResult:
    name: str
    ok: bool
    severity: str
    summary: str
    url: str = ""
    latency_ms: int | None = None
    details: list[str] = field(default_factory=list)


@dataclass
class RunReport:
    run_type: str
    started_at: datetime
    finished_at: datetime
    checks: list[CheckResult]
    council: str = ""
    improvements: str = ""
    notes_paths: list[str] = field(default_factory=list)
    issue_urls: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(check.ok for check in self.checks)

    @property
    def failures(self) -> list[CheckResult]:
        return [check for check in self.checks if not check.ok]

