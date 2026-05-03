# SpeakerAgent Ops Agent Instructions

This repo is a hosted operations agent, not a desktop automation script.

## Mission

Run safely on Railway and monitor SpeakerAgent.ai without depending on Lester's computer.

## Safety Rules

- Never auto-merge.
- Never auto-deploy.
- Never modify production environment variables.
- Never send outreach.
- Never store secrets in notes, Jira tickets, reports, or logs.
- Prefer Jira tickets, Slack reports, and Obsidian notes over direct code changes.

## Runtime Rules

- Keep checks deterministic where possible.
- AI council output is advisory only.
- Jira tickets are the handoff point for fixes.
- GitHub is for repositories, branches, pull requests, and optional Obsidian vault storage.
- Obsidian Markdown notes are the durable memory layer.
- Cursor SDK is intentionally not part of v1.

## Verification

Run:

```bash
pytest
python -m app.cli uptime
```

When editing Railway config, also verify:

```bash
python -m json.tool railway.json
```
