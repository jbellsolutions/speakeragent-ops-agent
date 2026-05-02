# SpeakerAgent Ops Agent

Always-on engineering operations agent for SpeakerAgent.ai.

This repo gives Lester a safe Railway-hosted monitor that checks the site and API, records issues, writes Obsidian-compatible infrastructure notes, and posts a daily Slack report at 4:00 a.m. Eastern.

It is intentionally conservative: it does **not** auto-merge, auto-deploy, or change production. It creates evidence, issues, reports, and improvement proposals so Codex or a human can fix the right thing with review.

## What It Checks

- Site runtime and uptime.
- API runtime when `TARGET_API_URL` is configured.
- Broken links from the public homepage.
- Browser smoke checks with headless Chromium.
- Browser console errors, page errors, and failed requests.
- Daily engineering suggestions.
- Daily skill/workflow improvement proposals.

## What It Produces

- Slack alert when a runtime check fails.
- Slack daily report every day at 4:00 a.m. Eastern.
- GitHub issues for runtime failures.
- Obsidian-compatible Markdown notes.
- Optional OpenAI-powered council reports when `OPENAI_API_KEY` is configured.

## Architecture Decision

Use Railway for always-on runtime.

Use deterministic checks first. Use OpenAI/Codex-style analysis second. Do not use Cursor SDK in v1.

Why:

- Railway is the safe hosted environment, so the agent is not running on Lester's computer.
- Deterministic uptime, link, and browser checks are more reliable than asking an AI if the site is up.
- GitHub Issues are the control plane for fixes.
- Obsidian Markdown notes are the memory layer.
- Cursor SDK can be reconsidered later, but it adds another paid runner, another API key, and another place for work to happen.

## Quick Start For Lester

### 1. Create The GitHub Repos

You need:

- This public repo for the ops agent.
- A repo where issues should be created, usually the ops agent repo or the main product repo.
- A private Obsidian notes repo, recommended name: `speakeragent-ops-vault`.

The Obsidian repo should be private if it may contain operational details.

### 2. Create Required Tokens

Create a GitHub fine-grained token with access to:

- The issue repo.
- The Obsidian notes repo.

Required permissions:

- Issues: read/write.
- Contents: read/write.
- Metadata: read.

Create a Slack incoming webhook for the channel where daily reports should land.

Optional: create an OpenAI API key if you want AI council and workflow-factory suggestions.

### 3. Deploy On Railway

1. Open Railway.
2. Create a new project.
3. Choose **Deploy from GitHub repo**.
4. Select this repo.
5. Railway will detect the Dockerfile and run the service.
6. Add the environment variables below.
7. Deploy.

Railway will use `railway.json` for the health check and restart policy.

### 4. Add Environment Variables

Minimum useful production setup:

```bash
TARGET_SITE_URL=https://speakeragent.ai/
TARGET_API_URL=
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
GITHUB_TOKEN=github_pat_...
GITHUB_ISSUES_REPO=jbellsolutions/speakeragent-ops-agent
OBSIDIAN_GITHUB_REPO=jbellsolutions/speakeragent-ops-vault
OBSIDIAN_GITHUB_BRANCH=main
OBSIDIAN_VAULT_PATH=SpeakerAgent Ops
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5.5
RUN_SCHEDULER=true
UPTIME_INTERVAL_SECONDS=300
DAILY_REPORT_HOUR_EASTERN=4
DRY_RUN=true
ADMIN_TOKEN=make-a-long-random-string
BROWSER_CHECK_ENABLED=true
MAX_LINKS=80
REQUEST_TIMEOUT_SECONDS=20
```

Start with `DRY_RUN=true`. That lets the service check the site and write local logs without creating GitHub issues or Obsidian commits. After `/status` looks correct, set:

```bash
DRY_RUN=false
```

### 5. Verify It Is Running

Open:

```text
https://YOUR-RAILWAY-DOMAIN/healthz
```

Expected response:

```json
{"ok":"true","service":"speakeragent-ops-agent"}
```

Then open:

```text
https://YOUR-RAILWAY-DOMAIN/status
```

That shows scheduler state, dry-run state, targets, and the latest report.

### 6. Trigger A Manual Daily Run

```bash
curl -X POST https://YOUR-RAILWAY-DOMAIN/run/daily \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### 7. Open Notes In Obsidian

Clone the private notes repo locally and open it as an Obsidian vault:

```bash
git clone https://github.com/jbellsolutions/speakeragent-ops-vault.git
```

The agent writes notes under:

```text
SpeakerAgent Ops/YYYY-MM-DD/
```

## Safety Model

This service can:

- Check runtime health.
- Check links.
- Run a headless browser smoke test.
- Create GitHub issues.
- Write Markdown notes.
- Post Slack messages.
- Generate suggestions.

This service cannot:

- Merge pull requests.
- Deploy production.
- Edit production environment variables.
- Send outreach emails.
- Change billing.
- Install Cursor agents.
- Run on Lester's computer.

## Codex, Cursor, Or A Different Harness?

For v1, use this Railway service plus GitHub Issues.

Codex should be used to work the issues, create PRs, review diffs, and improve the product. The always-on service should not try to be the coding agent itself.

Cursor SDK is not included in v1. It may be useful later for isolated cloud PR workers, but only after the deterministic monitoring and GitHub issue loop has proven itself.

## Local Development

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

Run one check locally:

```bash
python -m app.cli uptime
python -m app.cli daily
```

## Important Files

- `app/main.py` - FastAPI app and manual run endpoints.
- `app/scheduler.py` - uptime and daily scheduling loops.
- `app/checks.py` - HTTP, link, and browser checks.
- `app/runner.py` - orchestration for uptime and daily runs.
- `app/github_client.py` - GitHub issue and note file writes.
- `app/obsidian.py` - Obsidian Markdown storage.
- `docs/` - setup, safety, and runbooks.

## Railway Notes

Railway services are containers. This repo ships a Dockerfile, so Railway builds from the Dockerfile. The service is persistent and always running, not a Railway cron job, because it needs uptime checks throughout the day plus one daily report.

## License

MIT

