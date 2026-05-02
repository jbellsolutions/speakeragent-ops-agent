from __future__ import annotations

from datetime import UTC, datetime

from .ai import generate_council_report, generate_skill_factory_report
from .checks import run_runtime_checks
from .config import Settings
from .github_client import sync_failure_issues
from .models import RunReport
from .obsidian import write_note
from .reports import build_daily_markdown, build_runtime_markdown, slack_summary
from .slack import post_slack


async def run_uptime(settings: Settings) -> RunReport:
    started = datetime.now(UTC)
    checks = await run_runtime_checks(settings)
    runtime_markdown = build_runtime_markdown(settings, checks, started, "SpeakerAgent Runtime Report")
    issue_urls = await sync_failure_issues(
        settings,
        [check for check in checks if not check.ok],
        runtime_markdown,
    )
    note_path = await write_note(settings, "runtime-report", runtime_markdown, started)
    finished = datetime.now(UTC)
    report = RunReport(
        run_type="uptime",
        started_at=started,
        finished_at=finished,
        checks=checks,
        notes_paths=[note_path],
        issue_urls=issue_urls,
    )
    if not report.ok:
        await post_slack(settings, slack_summary(report))
    return report


async def run_daily(settings: Settings) -> RunReport:
    started = datetime.now(UTC)
    checks = await run_runtime_checks(settings)
    runtime_markdown = build_runtime_markdown(settings, checks, started, "SpeakerAgent Daily Runtime Report")
    council = await generate_council_report(settings, runtime_markdown)
    improvements = await generate_skill_factory_report(settings, runtime_markdown)
    issue_urls = await sync_failure_issues(
        settings,
        [check for check in checks if not check.ok],
        runtime_markdown,
    )

    finished = datetime.now(UTC)
    report = RunReport(
        run_type="daily",
        started_at=started,
        finished_at=finished,
        checks=checks,
        council=council,
        improvements=improvements,
        issue_urls=issue_urls,
    )
    daily_markdown = build_daily_markdown(report)
    report.notes_paths.append(await write_note(settings, "daily-engineering-report", daily_markdown, started))
    await post_slack(settings, slack_summary(report))
    return report

