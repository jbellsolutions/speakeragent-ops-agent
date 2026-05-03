from __future__ import annotations

import re
from dataclasses import dataclass

import httpx

from .config import Settings
from .models import CheckResult


def markdown_to_adf(markdown: str) -> dict[str, object]:
    blocks: list[dict[str, object]] = []
    for paragraph in markdown.strip().split("\n\n"):
        text = paragraph.strip()
        if not text:
            continue
        blocks.append(
            {
                "type": "paragraph",
                "content": [{"type": "text", "text": text[:32000]}],
            }
        )
    if not blocks:
        blocks.append({"type": "paragraph", "content": [{"type": "text", "text": "No details."}]})
    return {"type": "doc", "version": 1, "content": blocks}


def jira_label(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "-", value.strip().lower()).strip("-")
    return cleaned[:255]


def jira_labels(settings: Settings, check: CheckResult) -> list[str]:
    labels = [jira_label(item) for item in settings.jira_labels.split(",")]
    labels.append(jira_label(f"severity-{check.severity}"))
    return list(dict.fromkeys(label for label in labels if label))


def priority_for_check(settings: Settings, check: CheckResult) -> str:
    if check.severity == "critical":
        return settings.jira_priority_critical
    if check.severity == "warning":
        return settings.jira_priority_warning
    return settings.jira_priority_info


def issue_body_for_check(check: CheckResult, report_markdown: str) -> str:
    details = "\n".join(f"- {item}" for item in check.details) or "- No extra details"
    return f"""## Alert

`{check.name}` failed for `{check.url or 'configured target'}`.

Summary: {check.summary}

Severity: `{check.severity}`

## Details

{details}

## Latest Report

{report_markdown}

## Safety

This ops agent does not merge, deploy, or change production automatically. This Jira ticket is the handoff for Lester/Codex to inspect and fix.
"""


@dataclass
class JiraClient:
    base_url: str
    email: str
    api_token: str

    @property
    def root_url(self) -> str:
        return self.base_url.rstrip("/")

    @property
    def auth(self) -> httpx.BasicAuth:
        return httpx.BasicAuth(self.email, self.api_token)

    @property
    def headers(self) -> dict[str, str]:
        return {"Accept": "application/json", "Content-Type": "application/json"}

    def browse_url(self, key: str) -> str:
        return f"{self.root_url}/browse/{key}"

    async def find_open_issue(self, project_key: str, title: str, labels: list[str]) -> str | None:
        label_clause = f' AND labels = "{labels[0]}"' if labels else ""
        jql = f'project = "{project_key}" AND statusCategory != Done{label_clause} ORDER BY created DESC'
        async with httpx.AsyncClient(timeout=30, auth=self.auth, headers=self.headers) as client:
            response = await client.post(
                f"{self.root_url}/rest/api/3/search/jql",
                json={"jql": jql, "maxResults": 50, "fields": ["summary"]},
            )
            response.raise_for_status()
            for issue in response.json().get("issues", []):
                if issue.get("fields", {}).get("summary") == title:
                    return issue["key"]
        return None

    async def add_comment(self, issue_key: str, body: str) -> None:
        async with httpx.AsyncClient(timeout=30, auth=self.auth, headers=self.headers) as client:
            response = await client.post(
                f"{self.root_url}/rest/api/3/issue/{issue_key}/comment",
                json={"body": markdown_to_adf(body)},
            )
            response.raise_for_status()

    async def create_issue(
        self,
        project_key: str,
        issue_type: str,
        title: str,
        body: str,
        labels: list[str],
        component: str = "",
        priority: str = "",
    ) -> str:
        fields: dict[str, object] = {
            "project": {"key": project_key},
            "summary": title,
            "description": markdown_to_adf(body),
            "issuetype": {"name": issue_type},
            "labels": labels,
        }
        if component:
            fields["components"] = [{"name": component}]
        if priority:
            fields["priority"] = {"name": priority}

        async with httpx.AsyncClient(timeout=30, auth=self.auth, headers=self.headers) as client:
            response = await client.post(f"{self.root_url}/rest/api/3/issue", json={"fields": fields})
            response.raise_for_status()
            return response.json()["key"]

    async def ensure_issue(
        self,
        project_key: str,
        issue_type: str,
        title: str,
        body: str,
        labels: list[str],
        component: str = "",
        priority: str = "",
    ) -> str:
        issue_key = await self.find_open_issue(project_key, title, labels)
        if issue_key:
            await self.add_comment(issue_key, body)
            return self.browse_url(issue_key)

        issue_key = await self.create_issue(
            project_key,
            issue_type,
            title,
            body,
            labels,
            component=component,
            priority=priority,
        )
        return self.browse_url(issue_key)


async def sync_failure_jira_issues(
    settings: Settings,
    failures: list[CheckResult],
    report_markdown: str,
) -> list[str]:
    if not settings.can_write_jira:
        return []

    client = JiraClient(settings.jira_base_url, settings.jira_email, settings.jira_api_token)
    urls: list[str] = []
    for failure in failures:
        title = f"SpeakerAgent Ops Alert: {failure.name}"
        body = issue_body_for_check(failure, report_markdown)
        url = await client.ensure_issue(
            settings.jira_project_key,
            settings.jira_issue_type,
            title,
            body,
            jira_labels(settings, failure),
            component=settings.jira_component,
            priority=priority_for_check(settings, failure),
        )
        urls.append(url)
    return urls
