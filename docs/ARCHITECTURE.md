# Architecture

## Recommended Shape

SpeakerAgent Ops Agent is a Railway-hosted monitor and reporting service.

It is not the coding agent. It creates Jira tickets and evidence so Codex can safely do coding work through GitHub.

## Components

- FastAPI service for health, status, and manual trigger endpoints.
- In-process scheduler for uptime checks and daily reports.
- HTTP checks for site/API runtime.
- Link checker for broken public links.
- Playwright browser smoke test for page load, console errors, page errors, and failed requests.
- Jira ticket writer for failures.
- GitHub issue writer as a fallback only when Jira is not configured.
- GitHub-backed Obsidian note writer for reports and memory.
- Slack webhook delivery.
- Optional OpenAI council reports.

## Why Railway

Railway provides an always-on container service from a GitHub repo. This keeps the agent off Lester's laptop and gives a predictable hosted runtime.

## Why Not Cursor In V1

Cursor SDK is a runner, not the control plane. Adding it now would add an extra API key, billing surface, conventions, and failure modes before the basic monitoring-to-issue loop is proven.

## State Model

Durable state lives outside the Railway container:

- Jira tickets for operational problems.
- Obsidian Markdown notes in a GitHub repo for reports and memory.
- Slack for daily human-readable summaries.

Railway local disk is treated as ephemeral.

## Teams

The service runs three logical teams:

- Runtime team: uptime, API, browser, and link checks.
- Council team: daily subjective product/engineering suggestions.
- Skill factory team: daily workflow, skill, and test improvement proposals.

Only the runtime team can create operational failure tickets automatically. Council and skill factory output is advisory.
