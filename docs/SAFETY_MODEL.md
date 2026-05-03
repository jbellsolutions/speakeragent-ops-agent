# Safety Model

## Allowed

- Read public site and API endpoints.
- Run headless browser smoke checks.
- Create or update Jira tickets.
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

Runtime failures create Jira tickets when `DRY_RUN=false` and Jira is configured. GitHub Issues are fallback ticketing only.

Daily subjective recommendations are written to notes and Slack only. They do not become code or production changes automatically.

## Secret Handling

Do not put secrets in:

- Jira ticket bodies.
- Slack messages.
- Obsidian notes.
- Logs.
- Screenshots.

Secrets belong only in Railway environment variables.
