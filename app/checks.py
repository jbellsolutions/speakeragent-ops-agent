from __future__ import annotations

import asyncio
import time
from urllib.parse import urldefrag, urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from .config import Settings
from .models import CheckResult


async def check_http(name: str, url: str, settings: Settings) -> CheckResult:
    if not url:
        return CheckResult(name=name, ok=True, severity="info", summary="not configured")

    started = time.monotonic()
    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "SpeakerAgentOpsAgent/1.0"},
        ) as client:
            response = await client.get(url)
    except Exception as exc:
        return CheckResult(
            name=name,
            ok=False,
            severity="critical",
            url=url,
            summary=f"request failed: {exc}",
        )

    latency_ms = int((time.monotonic() - started) * 1000)
    ok = 200 <= response.status_code < 400
    return CheckResult(
        name=name,
        ok=ok,
        severity="critical" if not ok else "info",
        url=str(response.url),
        latency_ms=latency_ms,
        summary=f"HTTP {response.status_code}",
        details=[f"final_url={response.url}", f"bytes={len(response.content)}"],
    )


def extract_links(base_url: str, html: str, max_links: int) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urldefrag(urljoin(base_url, href))[0]
        parsed = urlparse(absolute)
        if parsed.scheme not in {"http", "https"}:
            continue
        if absolute not in seen:
            links.append(absolute)
            seen.add(absolute)
        if len(links) >= max_links:
            break
    return links


async def check_links(settings: Settings) -> CheckResult:
    try:
        async with httpx.AsyncClient(
            timeout=settings.request_timeout_seconds,
            follow_redirects=True,
            headers={"User-Agent": "SpeakerAgentOpsAgent/1.0"},
        ) as client:
            response = await client.get(settings.target_site_url)
            response.raise_for_status()
            links = extract_links(settings.target_site_url, response.text, settings.max_links)

            semaphore = asyncio.Semaphore(8)

            async def probe(url: str) -> tuple[str, int | str]:
                async with semaphore:
                    try:
                        result = await client.head(url)
                        if result.status_code in {405, 403}:
                            result = await client.get(url)
                        return url, result.status_code
                    except Exception as exc:
                        return url, str(exc)

            results = await asyncio.gather(*(probe(link) for link in links))
    except Exception as exc:
        return CheckResult(
            name="broken-links",
            ok=False,
            severity="high",
            url=settings.target_site_url,
            summary=f"link scan failed: {exc}",
        )

    broken = [
        f"{url} -> {status}"
        for url, status in results
        if not isinstance(status, int) or status >= 400
    ]
    return CheckResult(
        name="broken-links",
        ok=not broken,
        severity="high" if broken else "info",
        url=settings.target_site_url,
        summary=f"checked {len(results)} links, broken {len(broken)}",
        details=broken[:25],
    )


async def check_browser(settings: Settings) -> CheckResult:
    if not settings.browser_check_enabled:
        return CheckResult(name="browser-smoke", ok=True, severity="info", summary="disabled")

    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        return CheckResult(
            name="browser-smoke",
            ok=False,
            severity="medium",
            summary=f"Playwright unavailable: {exc}",
        )

    console_errors: list[str] = []
    request_failures: list[str] = []
    page_errors: list[str] = []

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()
            page = await browser.new_page()
            page.on(
                "console",
                lambda msg: console_errors.append(msg.text)
                if msg.type in {"error", "warning"}
                else None,
            )
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on(
                "requestfailed",
                lambda request: request_failures.append(
                    f"{request.url} -> {request.failure}"
                ),
            )
            response = await page.goto(
                settings.target_site_url,
                wait_until="networkidle",
                timeout=settings.request_timeout_seconds * 1000,
            )
            title = await page.title()
            await browser.close()
    except Exception as exc:
        return CheckResult(
            name="browser-smoke",
            ok=False,
            severity="critical",
            url=settings.target_site_url,
            summary=f"browser check failed: {exc}",
        )

    details = []
    details.extend(f"console: {item}" for item in console_errors[:10])
    details.extend(f"request: {item}" for item in request_failures[:10])
    details.extend(f"page: {item}" for item in page_errors[:10])
    status = response.status if response else None
    ok = bool(response and response.ok and not page_errors)
    return CheckResult(
        name="browser-smoke",
        ok=ok,
        severity="critical" if not ok else "info",
        url=settings.target_site_url,
        summary=f"status={status}, title={title!r}, console={len(console_errors)}, failed_requests={len(request_failures)}, page_errors={len(page_errors)}",
        details=details,
    )


async def run_runtime_checks(settings: Settings) -> list[CheckResult]:
    checks = [
        check_http("site-runtime", settings.target_site_url, settings),
        check_http("api-runtime", settings.target_api_url, settings),
        check_links(settings),
        check_browser(settings),
    ]
    return await asyncio.gather(*checks)

