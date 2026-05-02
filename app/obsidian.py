from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import Settings
from .github_client import GitHubClient


def safe_segment(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in " ._-" else "-" for ch in value).strip()


async def write_note(settings: Settings, kind: str, markdown: str, when: datetime) -> str:
    date_path = when.strftime("%Y-%m-%d")
    filename = f"{when.strftime('%H%M%S')}-{safe_segment(kind)}.md"
    relative_path = f"{settings.obsidian_vault_path}/{date_path}/{filename}"

    if settings.can_write_obsidian_github:
        client = GitHubClient(settings.github_token)
        return await client.put_file(
            settings.obsidian_github_repo,
            settings.obsidian_github_branch,
            relative_path,
            markdown,
            f"Add SpeakerAgent ops note: {kind} {date_path}",
        )

    local_path = Path("vault") / date_path / filename
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(markdown, encoding="utf-8")
    return str(local_path)

