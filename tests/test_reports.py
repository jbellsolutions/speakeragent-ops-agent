from __future__ import annotations

from datetime import UTC, datetime

from app.config import Settings
from app.models import CheckResult
from app.reports import build_runtime_markdown


def test_runtime_report_includes_failures():
    settings = Settings(
        target_site_url="https://speakeragent.ai/",
        target_api_url="",
        slack_webhook_url="",
        github_token="",
        github_issues_repo="",
        frontend_repo="",
        backend_repo="",
        obsidian_github_repo="",
        obsidian_github_branch="main",
        obsidian_vault_path="SpeakerAgent Ops",
        openai_api_key="",
        openai_model="gpt-5.5",
        run_scheduler=False,
        uptime_interval_seconds=300,
        daily_report_hour_eastern=4,
        dry_run=True,
        admin_token="",
        max_links=80,
        request_timeout_seconds=20,
        browser_check_enabled=True,
    )
    markdown = build_runtime_markdown(
        settings,
        [CheckResult(name="site-runtime", ok=False, severity="critical", summary="HTTP 500")],
        datetime.now(UTC),
        "Test Report",
    )
    assert "HTTP 500" in markdown
    assert "FAILED" in markdown

