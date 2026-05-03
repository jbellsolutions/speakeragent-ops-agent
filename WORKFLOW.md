---
name: speakeragent-jira-symphony-workflow
version: 1
tracker:
  kind: jira
  base_url_env: JIRA_BASE_URL
  project_key_env: JIRA_PROJECT_KEY
  issue_type_env: JIRA_ISSUE_TYPE
  labels_env: JIRA_LABELS
  status_contract:
    intake: "To Do"
    active: "In Progress"
    review: "Human Review"
    merge: "Ready to Merge"
    done: "Done"
runtime:
  hosted_monitor: railway
  poll_interval_seconds_env: UPTIME_INTERVAL_SECONDS
  daily_report_hour_eastern_env: DAILY_REPORT_HOUR_EASTERN
  max_parallel_ticket_workers: 2
  workspace_per_ticket: true
  default_runner: codex
repositories:
  frontend_repo_env: FRONTEND_REPO
  backend_repo_env: BACKEND_REPO
  notes_repo_env: OBSIDIAN_GITHUB_REPO
handoff:
  create_prs: true
  merge_prs: false
  deploy_production: false
  require_human_review: true
verification:
  require_test_output: true
  require_browser_evidence_for_frontend: true
  require_jira_progress_comments: true
  write_obsidian_notes: true
future_runners:
  cursor_sdk: evaluate_later
---

# SpeakerAgent Jira Workflow

This is the repo-owned operating contract for SpeakerAgent's Symphony-style engineering workflow.

The key adaptation: Jira is the control plane. Do not use Linear for this project. Do not use GitHub Issues unless Jira is unavailable and `GITHUB_ISSUES_REPO` has intentionally been configured as a fallback.

## Mission

Run SpeakerAgent engineering operations through Jira tickets, GitHub PRs, Slack reports, and Obsidian memory.

The Railway service watches production and creates operational Jira tickets. Codex ticket workers use those tickets as the durable source of truth, work in isolated branches or worktrees, post progress back to Jira, and produce reviewable PRs with proof.

## Jira State Machine

Use these Jira statuses for the agent workflow:

- `To Do`: eligible for a Codex worker.
- `In Progress`: a worker is actively investigating or implementing.
- `Human Review`: implementation is complete enough for Lester or another human to inspect.
- `Ready to Merge`: human has approved the direction and the PR is ready for final merge handling.
- `Done`: the fix is merged, deployed when needed, and verified.

If the Jira project uses different status names, map them to the same meanings. The workflow meaning matters more than the literal label.

## Ticket Intake Rules

A ticket is ready for Codex when it has:

- a clear problem or goal,
- affected surface, such as frontend, backend, API, monitoring, docs, or workflow,
- expected outcome,
- links to relevant reports, logs, screenshots, or Obsidian notes when available,
- a priority or severity label when known.

Runtime failure tickets created by Railway are valid intake tickets even if they are terse, because the linked report carries the evidence.

## Worker Rules

For each Jira ticket:

1. Read the full Jira ticket and linked notes.
2. Identify the target repo: frontend, backend, ops-agent, or notes.
3. Create an isolated branch or worktree named from the Jira key.
4. Post a short Jira comment with the plan before changing code.
5. Make the smallest coherent change that solves the ticket.
6. Run the strongest practical verification.
7. Post a proof packet to Jira.
8. Open a GitHub PR when code changed.
9. Move the Jira ticket to `Human Review`.

Never merge, deploy production, modify production secrets, or mark a ticket `Done` without human approval.

## Proof Packet

Every implementation ticket should end with a Jira comment containing:

- summary of what changed,
- PR link when code changed,
- tests or checks run,
- browser evidence for frontend work,
- remaining risks or follow-up tickets,
- Obsidian note path when a durable note was written.

Frontend proof should include a browser smoke check. When video capture is available, attach or link the recording from the ticket. If video capture is unavailable, include the exact browser path tested, console/network findings, and screenshots or trace references.

## Daily Council Rules

The daily council is advisory. It may propose:

- product improvements,
- UX cleanup,
- backend/API hardening,
- monitoring expansion,
- test coverage,
- new Codex skills or workflows.

The daily council may write notes and suggest tickets. It must not auto-promote suggestions into production changes.

## Skill Factory Rules

The skill factory looks for repeated failure modes and turns them into reusable procedures.

Good skill candidates:

- repeated setup steps,
- common debugging flows,
- recurring Jira ticket patterns,
- production log review flows,
- browser verification routines,
- launch smoke tests.

New skills must be proposed, tested, and reviewed before they become expected runtime behavior.

## Runner Policy

OpenAI Codex is the default runner.

Cursor SDK remains a future evaluation option only. Add it only after the Jira control plane has processed real tickets and there is evidence that Cursor reduces review or implementation time enough to justify another runtime, API key, and billing surface.

## Done Definition

A Jira ticket is done only when:

- the root issue has been addressed or explicitly deferred,
- verification evidence exists,
- any GitHub PR has been reviewed and merged manually,
- production has been checked when production behavior changed,
- follow-up work has separate Jira tickets,
- notes are stored in Obsidian when the decision or investigation should persist.
