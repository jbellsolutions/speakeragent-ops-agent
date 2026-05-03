from __future__ import annotations

import os
from dataclasses import dataclass


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return int(value)


def env_str(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


@dataclass(frozen=True)
class Settings:
    target_site_url: str
    target_api_url: str
    slack_webhook_url: str
    github_token: str
    github_issues_repo: str
    jira_base_url: str
    jira_email: str
    jira_api_token: str
    jira_project_key: str
    jira_issue_type: str
    jira_labels: str
    jira_component: str
    jira_priority_critical: str
    jira_priority_warning: str
    jira_priority_info: str
    frontend_repo: str
    backend_repo: str
    obsidian_github_repo: str
    obsidian_github_branch: str
    obsidian_vault_path: str
    openai_api_key: str
    openai_model: str
    run_scheduler: bool
    uptime_interval_seconds: int
    daily_report_hour_eastern: int
    dry_run: bool
    admin_token: str
    max_links: int
    request_timeout_seconds: int
    browser_check_enabled: bool

    @property
    def can_write_github_issues(self) -> bool:
        return bool(self.github_token and self.github_issues_repo and not self.dry_run)

    @property
    def can_write_jira(self) -> bool:
        return bool(
            self.jira_base_url
            and self.jira_email
            and self.jira_api_token
            and self.jira_project_key
            and not self.dry_run
        )

    @property
    def ticket_backend(self) -> str:
        if self.can_write_jira:
            return "jira"
        if self.can_write_github_issues:
            return "github-issues"
        return "disabled"

    @property
    def can_write_obsidian_github(self) -> bool:
        return bool(self.github_token and self.obsidian_github_repo and not self.dry_run)

    @property
    def can_post_slack(self) -> bool:
        return bool(self.slack_webhook_url)

    @property
    def can_use_ai(self) -> bool:
        return bool(self.openai_api_key)


def load_settings() -> Settings:
    return Settings(
        target_site_url=env_str("TARGET_SITE_URL", "https://speakeragent.ai/"),
        target_api_url=env_str("TARGET_API_URL"),
        slack_webhook_url=env_str("SLACK_WEBHOOK_URL"),
        github_token=env_str("GITHUB_TOKEN"),
        github_issues_repo=env_str("GITHUB_ISSUES_REPO"),
        jira_base_url=env_str("JIRA_BASE_URL"),
        jira_email=env_str("JIRA_EMAIL"),
        jira_api_token=env_str("JIRA_API_TOKEN"),
        jira_project_key=env_str("JIRA_PROJECT_KEY"),
        jira_issue_type=env_str("JIRA_ISSUE_TYPE", "Bug"),
        jira_labels=env_str("JIRA_LABELS", "speakeragent-ops,monitoring"),
        jira_component=env_str("JIRA_COMPONENT"),
        jira_priority_critical=env_str("JIRA_PRIORITY_CRITICAL"),
        jira_priority_warning=env_str("JIRA_PRIORITY_WARNING"),
        jira_priority_info=env_str("JIRA_PRIORITY_INFO"),
        frontend_repo=env_str("FRONTEND_REPO"),
        backend_repo=env_str("BACKEND_REPO"),
        obsidian_github_repo=env_str("OBSIDIAN_GITHUB_REPO"),
        obsidian_github_branch=env_str("OBSIDIAN_GITHUB_BRANCH", "main"),
        obsidian_vault_path=env_str("OBSIDIAN_VAULT_PATH", "SpeakerAgent Ops"),
        openai_api_key=env_str("OPENAI_API_KEY"),
        openai_model=env_str("OPENAI_MODEL", "gpt-5.5"),
        run_scheduler=env_bool("RUN_SCHEDULER", True),
        uptime_interval_seconds=env_int("UPTIME_INTERVAL_SECONDS", 300),
        daily_report_hour_eastern=env_int("DAILY_REPORT_HOUR_EASTERN", 4),
        dry_run=env_bool("DRY_RUN", True),
        admin_token=env_str("ADMIN_TOKEN"),
        max_links=env_int("MAX_LINKS", 80),
        request_timeout_seconds=env_int("REQUEST_TIMEOUT_SECONDS", 20),
        browser_check_enabled=env_bool("BROWSER_CHECK_ENABLED", True),
    )
