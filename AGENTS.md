# SpeakerAgent Ops Agent Instructions

This repo is a hosted operations agent, not a desktop automation script.

## Mission

Run safely on Railway and monitor SpeakerAgent.ai without depending on Lester's computer.

## Safety Rules

- Never auto-merge.
- Never auto-deploy.
- Never modify production environment variables.
- Never send outreach.
- Never store secrets in notes, issues, reports, or logs.
- Prefer GitHub issues, Slack reports, and Obsidian notes over direct code changes.

## Runtime Rules

- Keep checks deterministic where possible.
- AI council output is advisory only.
- GitHub Issues are the handoff point for fixes.
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

