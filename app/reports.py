from __future__ import annotations

from datetime import datetime

from .config import Settings
from .models import CheckResult, RunReport


def format_check(check: CheckResult) -> str:
    status = "PASS" if check.ok else "FAIL"
    latency = f" ({check.latency_ms}ms)" if check.latency_ms is not None else ""
    details = "\n".join(f"  - {item}" for item in check.details[:20])
    detail_block = f"\n{details}" if details else ""
    return f"- **{status}** `{check.name}` [{check.severity}]{latency}: {check.summary}{detail_block}"


def build_runtime_markdown(settings: Settings, checks: list[CheckResult], started_at: datetime, title: str) -> str:
    failures = [check for check in checks if not check.ok]
    status = "FAILED" if failures else "PASSED"
    lines = [
        f"# {title}",
        "",
        f"- Target site: `{settings.target_site_url}`",
        f"- API target: `{settings.target_api_url or 'not configured'}`",
        f"- Started: `{started_at.isoformat()}`",
        f"- Status: `{status}`",
        f"- Dry run: `{settings.dry_run}`",
        "",
        "## Checks",
        "",
    ]
    lines.extend(format_check(check) for check in checks)
    return "\n".join(lines) + "\n"


def build_daily_markdown(report: RunReport) -> str:
    lines = [
        "# SpeakerAgent Daily Engineering Report",
        "",
        f"- Started: `{report.started_at.isoformat()}`",
        f"- Finished: `{report.finished_at.isoformat()}`",
        f"- Status: `{'PASSED' if report.ok else 'FAILED'}`",
        "",
        "## Runtime Checks",
        "",
    ]
    lines.extend(format_check(check) for check in report.checks)
    if report.council:
        lines.extend(["", "## Council Suggestions", "", report.council])
    if report.improvements:
        lines.extend(["", "## Skill And Workflow Factory", "", report.improvements])
    if report.issue_urls:
        lines.extend(["", "## GitHub Issues", ""])
        lines.extend(f"- {url}" for url in report.issue_urls)
    if report.notes_paths:
        lines.extend(["", "## Obsidian Notes", ""])
        lines.extend(f"- {path}" for path in report.notes_paths)
    return "\n".join(lines) + "\n"


def slack_summary(report: RunReport) -> str:
    status = "PASSED" if report.ok else "FAILED"
    failures = "\n".join(f"- {item.name}: {item.summary}" for item in report.failures[:10])
    issues = "\n".join(f"- {url}" for url in report.issue_urls[:10])
    notes = "\n".join(f"- {path}" for path in report.notes_paths[:5])
    return f"""SpeakerAgent Ops Report: {status}

Runtime failures:
{failures or "- None"}

Issues:
{issues or "- None created"}

Notes:
{notes or "- None written"}
"""

