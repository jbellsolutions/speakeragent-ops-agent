from __future__ import annotations

import httpx

from .config import Settings


async def post_slack(settings: Settings, text: str) -> str:
    if not settings.slack_webhook_url:
        return "skipped: SLACK_WEBHOOK_URL not configured"
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(settings.slack_webhook_url, json={"text": text})
        response.raise_for_status()
    return "posted"

