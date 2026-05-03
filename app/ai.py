from __future__ import annotations

import httpx

from .config import Settings


def deterministic_council(report_markdown: str) -> str:
    return f"""## Council Review

AI council is not configured because `OPENAI_API_KEY` is missing.

Default recommendations:

- Fix any failed runtime, API, browser, or broken-link checks first.
- Keep autonomous changes limited to Jira tickets and draft plans until the repo has reliable tests.
- Add missing smoke tests for signup, onboarding, dashboard, and lead approval.
- Keep production deploys manual until rollback and verification are documented.

## Input Reviewed

{report_markdown[:3000]}
"""


async def ask_openai(settings: Settings, prompt: str) -> str:
    if not settings.can_use_ai:
        return deterministic_council(prompt)

    payload = {
        "model": settings.openai_model,
        "input": prompt,
    }
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.openai.com/v1/responses",
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    if data.get("output_text"):
        return str(data["output_text"])

    chunks: list[str] = []
    for item in data.get("output", []):
        for content in item.get("content", []):
            if content.get("type") in {"output_text", "text"} and content.get("text"):
                chunks.append(str(content["text"]))
    return "\n".join(chunks).strip() or deterministic_council(prompt)


async def generate_council_report(settings: Settings, report_markdown: str) -> str:
    prompt = f"""You are the SpeakerAgent engineering council.

Review this daily ops report and return:

1. Production risks.
2. Product/UX improvements.
3. Backend/API improvements.
4. Monitoring/test improvements.
5. New skills or workflows worth proposing.

Rules:
- Do not recommend autonomous deploys.
- Prefer Jira tickets, draft PRs, and Obsidian notes.
- Keep the report concise and actionable.

Report:

{report_markdown}
"""
    return await ask_openai(settings, prompt)


async def generate_skill_factory_report(settings: Settings, report_markdown: str) -> str:
    prompt = f"""You are the SpeakerAgent skill factory.

Look at this ops report and propose new agent skills, workflows, or checklists that would improve the system.

Return only proposals that can be tested safely. Do not install plugins or change runtime behavior automatically.

Report:

{report_markdown}
"""
    return await ask_openai(settings, prompt)
