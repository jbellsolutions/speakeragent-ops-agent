# Obsidian Notes Backend

## Recommended Setup

Create a private GitHub repo:

```text
jbellsolutions/speakeragent-ops-vault
```

Open that repo as an Obsidian vault locally.

Configure Railway:

```bash
OBSIDIAN_GITHUB_REPO=jbellsolutions/speakeragent-ops-vault
OBSIDIAN_GITHUB_BRANCH=main
OBSIDIAN_VAULT_PATH=SpeakerAgent Ops
```

## Note Structure

The service writes:

```text
SpeakerAgent Ops/
  YYYY-MM-DD/
    HHMMSS-runtime-report.md
    HHMMSS-daily-engineering-report.md
```

## Why GitHub-Backed Notes

Railway local disk is ephemeral. GitHub gives durable notes that can be opened in Obsidian and reviewed over time.

## Dry Run

When `DRY_RUN=true`, notes are written only to local `vault/` inside the container. That is useful for testing but not durable.

