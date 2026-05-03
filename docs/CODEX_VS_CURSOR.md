# Codex, Cursor, Or Another Harness?

## Decision

Use the Railway ops agent plus Jira for always-on monitoring.

Use Codex to work Jira tickets and create reviewed GitHub PRs.

Do not use Cursor SDK in v1.

Use [`WORKFLOW.md`](../WORKFLOW.md) as the repo-owned Symphony-style ticket workflow for Codex workers.

## Why

The always-on job needs reliable monitoring, durable state, Slack reports, and Jira ticket creation. Deterministic code is better for that than a coding agent loop.

Codex is useful after a failure is found:

- inspect frontend/backend code,
- create a branch,
- add tests,
- open a PR,
- produce verification evidence.

Cursor SDK may be useful later for parallel cloud coding workers, but it is not needed to prove the operations loop.

## Reconsider Cursor When

- Frontend and backend repos are confirmed.
- Five real Jira tickets have gone through intake to proof packet.
- Codex runner limitations are documented.
- Cursor billing and API access are acceptable.
- Cursor materially reduces time to reviewed PR.
