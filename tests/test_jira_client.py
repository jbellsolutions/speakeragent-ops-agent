from __future__ import annotations

from app.config import Settings
from app.jira_client import jira_label, jira_labels, markdown_to_adf
from app.models import CheckResult


def test_jira_label_sanitizes_values():
    assert jira_label("severity:critical") == "severity-critical"
    assert jira_label(" SpeakerAgent Ops ") == "speakeragent-ops"


def test_markdown_to_adf_uses_document_format():
    adf = markdown_to_adf("## Alert\n\nSomething failed.")
    assert adf["type"] == "doc"
    assert adf["version"] == 1
    assert adf["content"][0]["type"] == "paragraph"


def test_jira_labels_keep_base_labels_first():
    settings = Settings(
        target_site_url="https://speakeragent.ai/",
        target_api_url="",
        slack_webhook_url="",
        github_token="",
        github_issues_repo="",
        jira_base_url="https://example.atlassian.net",
        jira_email="ops@example.com",
        jira_api_token="token",
        jira_project_key="SA",
        jira_issue_type="Bug",
        jira_labels="speakeragent-ops,monitoring",
        jira_component="",
        jira_priority_critical="",
        jira_priority_warning="",
        jira_priority_info="",
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
        dry_run=False,
        admin_token="",
        max_links=80,
        request_timeout_seconds=20,
        browser_check_enabled=True,
    )
    check = CheckResult(name="site-runtime", ok=False, severity="critical", summary="HTTP 500")

    assert jira_labels(settings, check) == ["speakeragent-ops", "monitoring", "severity-critical"]
    assert settings.ticket_backend == "jira"
