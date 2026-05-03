# Jira Setup

Jira is the default ticketing system for SpeakerAgent Ops Agent.

## Required Project

Use one Jira project as the operational queue for SpeakerAgent. Recommended setup:

- Project key: `SA` or the existing SpeakerAgent project key.
- Issue type: `Bug` for runtime failures, or `Task` if the project does not use bugs.
- Labels: `speakeragent-ops`, `monitoring`.

## Symphony-Style Statuses

The recommended Jira board statuses are:

```text
To Do
In Progress
Human Review
Ready to Merge
Done
```

If the existing Jira board uses different names, keep the same meanings:

- intake,
- active work,
- human review,
- merge-ready,
- complete.

The agent deduplicates tickets by open issue title. When the same check fails again, it adds a comment to the existing open ticket instead of creating a duplicate.

## Railway Variables

```bash
JIRA_BASE_URL=https://example.atlassian.net
JIRA_EMAIL=ops@example.com
JIRA_API_TOKEN=
JIRA_PROJECT_KEY=SA
JIRA_ISSUE_TYPE=Bug
JIRA_LABELS=speakeragent-ops,monitoring
JIRA_COMPONENT=
JIRA_PRIORITY_CRITICAL=
JIRA_PRIORITY_WARNING=
JIRA_PRIORITY_INFO=
```

Leave priority fields blank unless the Jira project already has matching priority names. If the project uses standard names, useful mappings are:

```bash
JIRA_PRIORITY_CRITICAL=High
JIRA_PRIORITY_WARNING=Medium
JIRA_PRIORITY_INFO=Low
```

## Token Scope

Use an Atlassian API token for the Railway service account. The account needs permission to browse the project, create issues, and add comments.

## GitHub Relationship

GitHub remains the code layer:

- frontend repo,
- backend repo,
- branches,
- pull requests,
- optional Obsidian vault storage.

Do not use Linear for this workflow. Do not use GitHub Issues unless Jira is unavailable and `GITHUB_ISSUES_REPO` has intentionally been configured as a fallback.

## Workflow Contract

The repo-owned contract for ticket workers is [`WORKFLOW.md`](../WORKFLOW.md). Keep Jira status names, proof requirements, and runner policy aligned with that file.
