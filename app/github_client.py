from __future__ import annotations

import base64
from dataclasses import dataclass
from urllib.parse import quote

import httpx

from .config import Settings
from .models import CheckResult


GITHUB_API = "https://api.github.com"


@dataclass
class GitHubClient:
    token: str

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def ensure_issue(self, repo: str, title: str, body: str, labels: list[str]) -> str:
        async with httpx.AsyncClient(timeout=30, headers=self.headers) as client:
            query = quote(f'repo:{repo} is:issue is:open in:title "{title}"')
            search = await client.get(f"{GITHUB_API}/search/issues?q={query}")
            search.raise_for_status()
            items = search.json().get("items", [])
            if items:
                number = items[0]["number"]
                comment = await client.post(
                    f"{GITHUB_API}/repos/{repo}/issues/{number}/comments",
                    json={"body": body},
                )
                comment.raise_for_status()
                return items[0]["html_url"]

            created = await client.post(
                f"{GITHUB_API}/repos/{repo}/issues",
                json={"title": title, "body": body, "labels": labels},
            )
            created.raise_for_status()
            return created.json()["html_url"]

    async def put_file(
        self,
        repo: str,
        branch: str,
        path: str,
        content: str,
        message: str,
    ) -> str:
        async with httpx.AsyncClient(timeout=30, headers=self.headers) as client:
            sha = None
            current = await client.get(
                f"{GITHUB_API}/repos/{repo}/contents/{quote(path)}",
                params={"ref": branch},
            )
            if current.status_code == 200:
                sha = current.json().get("sha")
            elif current.status_code != 404:
                current.raise_for_status()

            payload = {
                "message": message,
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "branch": branch,
            }
            if sha:
                payload["sha"] = sha

            result = await client.put(
                f"{GITHUB_API}/repos/{repo}/contents/{quote(path)}",
                json=payload,
            )
            result.raise_for_status()
            return result.json()["content"]["html_url"]


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

This ops agent does not merge, deploy, or change production automatically. This fallback GitHub issue is the handoff for Lester/Codex only when Jira is unavailable.
"""


async def sync_failure_github_issues(
    settings: Settings,
    failures: list[CheckResult],
    report_markdown: str,
) -> list[str]:
    if not settings.can_write_github_issues:
        return []
    client = GitHubClient(settings.github_token)
    urls: list[str] = []
    for failure in failures:
        title = f"SpeakerAgent Ops Alert: {failure.name}"
        body = issue_body_for_check(failure, report_markdown)
        url = await client.ensure_issue(
            settings.github_issues_repo,
            title,
            body,
            ["ops-agent", "monitoring", f"severity:{failure.severity}"],
        )
        urls.append(url)
    return urls
