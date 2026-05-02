# Safety Model

## Allowed

- Read public site and API endpoints.
- Run headless browser smoke checks.
- Create or update GitHub issues.
- Write Markdown reports to an Obsidian notes repo.
- Post Slack reports.
- Generate advisory recommendations.

## Not Allowed

- Merge PRs.
- Deploy production.
- Modify production env vars.
- Send outreach emails.
- Change billing.
- Auto-install plugins.
- Auto-promote new skills into runtime behavior.

## Failure Handling

Runtime failures create GitHub issues when `DRY_RUN=false`.

Daily subjective recommendations are written to notes and Slack only. They do not become code or production changes automatically.

## Secret Handling

Do not put secrets in:

- GitHub issue bodies.
- Slack messages.
- Obsidian notes.
- Logs.
- Screenshots.

Secrets belong only in Railway environment variables.

