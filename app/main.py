from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException

from .config import Settings, load_settings
from .reports import build_daily_markdown
from .scheduler import OpsScheduler


settings = load_settings()
scheduler = OpsScheduler(settings)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.run_scheduler:
        scheduler.start()
    yield
    await scheduler.stop()


app = FastAPI(title="SpeakerAgent Ops Agent", version="1.0.0", lifespan=lifespan)


def require_admin(authorization: str | None = Header(default=None)) -> None:
    if not settings.admin_token:
        raise HTTPException(status_code=403, detail="ADMIN_TOKEN is not configured")
    expected = f"Bearer {settings.admin_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="invalid admin token")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"ok": "true", "service": "speakeragent-ops-agent"}


@app.get("/status")
async def status() -> dict[str, object]:
    report = scheduler.last_report
    return {
        "scheduler": settings.run_scheduler,
        "dry_run": settings.dry_run,
        "target_site_url": settings.target_site_url,
        "target_api_url": settings.target_api_url or None,
        "last_report": None
        if not report
        else {
            "run_type": report.run_type,
            "ok": report.ok,
            "started_at": report.started_at.isoformat(),
            "finished_at": report.finished_at.isoformat(),
            "failures": [failure.name for failure in report.failures],
        },
    }


@app.post("/run/uptime", dependencies=[Depends(require_admin)])
async def run_uptime_now() -> dict[str, object]:
    report = await scheduler.run_uptime_now()
    return {"ok": report.ok, "failures": [failure.name for failure in report.failures]}


@app.post("/run/daily", dependencies=[Depends(require_admin)])
async def run_daily_now() -> dict[str, object]:
    report = await scheduler.run_daily_now()
    return {
        "ok": report.ok,
        "markdown": build_daily_markdown(report),
        "issues": report.issue_urls,
        "notes": report.notes_paths,
    }

