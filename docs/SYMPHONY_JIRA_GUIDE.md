# Symphony Jira Guide

This repo adapts OpenAI Symphony's ticket-level orchestration model to SpeakerAgent's Jira workflow.

Source guide:

- Video: [OpenAI Symphony walkthrough](https://www.youtube.com/watch?v=M_AmPWmkpwA)
- OpenAI post: [An open-source spec for Codex orchestration: Symphony](https://openai.com/index/open-source-codex-orchestration-symphony/)
- Reference repo: [openai/symphony](https://github.com/openai/symphony)

## What We Are Taking From Symphony

The useful pattern is not the specific ticket tool. The useful pattern is:

- work is managed as tickets, not live chat sessions,
- the ticket tracker is the durable state machine,
- each ticket gets an isolated workspace,
- the workflow contract lives in the repo as Markdown,
- agents report progress back to the ticket,
- humans review proof packets instead of supervising every step,
- automated checks and browser evidence matter as much as the code change.

## SpeakerAgent Adaptation

SpeakerAgent uses Jira instead of Linear.

| Symphony Concept | SpeakerAgent Version |
| --- | --- |
| Linear project | Jira project |
| Linear issue | Jira ticket |
| Linear status | Jira workflow status |
| Symphony daemon | Railway ops monitor plus Codex ticket workers |
| `WORKFLOW.md` | [`WORKFLOW.md`](../WORKFLOW.md) |
| Agent update comments | Jira comments |
| Review packet | Jira proof packet plus GitHub PR |
| Persistent learning | Obsidian notes repo |

## Jira Status Contract

Use these statuses or map existing Jira statuses to the same meanings:

- `To Do`: ready for a worker.
- `In Progress`: a worker is active.
- `Human Review`: work is ready for human inspection.
- `Ready to Merge`: human approval has happened and the PR can be merged manually.
- `Done`: merged, deployed if needed, and verified.

This keeps Jira as the control plane without requiring Linear.

## Railway Service Role

The Railway service is the always-on monitor. It should:

- check uptime,
- check API health,
- scan public broken links,
- run browser smoke checks,
- create or update Jira tickets for failures,
- write reports to Obsidian,
- post Slack alerts and daily reports.

The Railway service should not:

- merge PRs,
- deploy production,
- change production secrets,
- become a general-purpose coding agent.

## Codex Worker Role

Codex works the Jira tickets. A worker should:

- read the Jira ticket and linked Obsidian notes,
- create an isolated branch or worktree,
- post a Jira plan comment,
- implement the fix or investigation,
- run verification,
- open a GitHub PR when code changes,
- post a proof packet back to Jira,
- move the ticket to `Human Review`.

## Proof Packet Standard

A useful Jira proof packet includes:

- PR link,
- summary of code or investigation,
- tests/checks run,
- browser evidence for frontend work,
- logs or report links,
- remaining risks,
- follow-up Jira tickets when needed.

For frontend work, browser evidence should include the route tested and console/network findings. Video evidence is preferred when available, but screenshots, traces, and concise test output are acceptable for v1.

## Skills And Self-Verification

The video emphasizes that orchestration only works when the repo is agent-ready. For SpeakerAgent that means:

- startup commands are documented,
- env setup is clear,
- tests are easy to run,
- browser checks are scripted,
- production log access has a safe read-only path,
- Jira operations are documented,
- proof requirements are explicit.

The daily skill factory should look for repeated manual steps and propose new skills or workflows. Those proposals stay advisory until tested and reviewed.

## Cursor SDK Decision

Do not add Cursor SDK in v1.

The Jira control plane, Railway monitor, Obsidian notes, and Codex PR workflow need to prove themselves first. Reconsider Cursor SDK only after at least five real Jira tickets have gone through intake, implementation, proof, review, and merge handling.
