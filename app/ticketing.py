from __future__ import annotations

from .config import Settings
from .github_client import sync_failure_github_issues
from .jira_client import sync_failure_jira_issues
from .models import CheckResult


async def sync_failure_tickets(
    settings: Settings,
    failures: list[CheckResult],
    report_markdown: str,
) -> list[str]:
    if settings.can_write_jira:
        return await sync_failure_jira_issues(settings, failures, report_markdown)
    if settings.can_write_github_issues:
        return await sync_failure_github_issues(settings, failures, report_markdown)
    return []
