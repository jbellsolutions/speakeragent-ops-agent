# Railway Setup

## Deploy

1. Open Railway.
2. Create a new project.
3. Deploy from this GitHub repo:

```text
https://github.com/jbellsolutions/speakeragent-ops-agent
```

4. Add environment variables from `.env.example`.
5. Deploy the service.

This repo includes:

- `Dockerfile`
- `railway.json`
- `/healthz` health endpoint

Railway will build the Dockerfile and use `/healthz` for health checks.

## Recommended Railway Settings

- One replica.
- Restart policy: always.
- Public networking enabled.
- No volume required if `OBSIDIAN_GITHUB_REPO` is configured.

## Required Variables

```bash
TARGET_SITE_URL=https://speakeragent.ai/
SLACK_WEBHOOK_URL=
GITHUB_TOKEN=
GITHUB_ISSUES_REPO=
ADMIN_TOKEN=
```

## Recommended Variables

```bash
OBSIDIAN_GITHUB_REPO=
OPENAI_API_KEY=
TARGET_API_URL=
DRY_RUN=false
```

## First Launch

Start with:

```bash
DRY_RUN=true
```

Verify:

```text
/healthz
/status
```

Then set:

```bash
DRY_RUN=false
```

Manual test:

```bash
curl -X POST https://YOUR-RAILWAY-DOMAIN/run/daily \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```
