# Runbook

## If The Site Is Down

1. Check Slack report.
2. Open the GitHub issue created by the ops agent.
3. Check Railway/Vercel deployment logs for the frontend and backend.
4. Ask Codex to inspect the failing repo and create a PR.
5. Verify the fix.
6. Merge manually.
7. Confirm the next uptime check passes.

## If Slack Stops Posting

1. Check `SLACK_WEBHOOK_URL`.
2. Trigger `/run/daily`.
3. Check Railway logs.
4. Confirm Slack app/webhook is still active.

## If Notes Stop Appearing

1. Check `OBSIDIAN_GITHUB_REPO`.
2. Check `GITHUB_TOKEN` contents permission.
3. Confirm the target branch exists.
4. Check Railway logs for GitHub API errors.

## If Too Many Issues Are Created

The issue writer deduplicates by alert title. If noise is high:

1. Increase `UPTIME_INTERVAL_SECONDS`.
2. Lower `MAX_LINKS`.
3. Disable browser checks temporarily with `BROWSER_CHECK_ENABLED=false`.
4. Add a specific known noisy URL to future ignore logic.

