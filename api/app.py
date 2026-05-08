from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from core.engine import ScanEngine
from core.storage import Storage

app = FastAPI(title="CyberRecon AI API", version="1.0.0")
engine = ScanEngine(portable=True)
storage = Storage()

active_jobs: dict[str, dict[str, Any]] = {}


class ScanRequest(BaseModel):
    target: str
    full: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/scans")
async def create_scan(request: ScanRequest) -> dict[str, Any]:
    job_id = f"job-{len(active_jobs) + 1}"
    active_jobs[job_id] = {"status": "running", "target": request.target, "result": None}

    async def run() -> None:
        try:
            result = await engine.scan(request.target, full=request.full)
            active_jobs[job_id]["status"] = "completed"
            active_jobs[job_id]["result"] = result
        except Exception as exc:
            active_jobs[job_id]["status"] = "failed"
            active_jobs[job_id]["result"] = {"error": str(exc)}

    asyncio.create_task(run())
    return {"job_id": job_id, "status": "running"}


@app.get("/scans/{job_id}")
def scan_status(job_id: str) -> dict[str, Any]:
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="job not found")
    return active_jobs[job_id]


@app.get("/findings/{scan_id}")
def findings(scan_id: int) -> list[dict[str, Any]]:
    return storage.scan_findings(scan_id)


@app.get("/reports/{target}")
def reports(target: str) -> dict[str, str]:
    report_dir = Path("reports")
    artifacts = {
        "json": report_dir / f"{target}_report.json",
        "markdown": report_dir / f"{target}_report.md",
        "html": report_dir / f"{target}_report.html",
    }
    response = {k: str(v) for k, v in artifacts.items() if v.exists()}
    if not response:
        raise HTTPException(status_code=404, detail="no reports found")
    return response


@app.get("/screenshots/{target}")
def screenshot_gallery(target: str) -> dict[str, Any]:
    path = Path("output") / target / "screenshots" / target
    if not path.exists():
        return {"target": target, "screenshots": []}
    files = [str(p) for p in path.glob("*.png")]
    return {"target": target, "screenshots": sorted(files)}


@app.get("/statistics")
def statistics() -> dict[str, Any]:
    scans = storage.recent_scans(limit=200)
    completed = [s for s in scans if s["status"] == "completed"]
    return {
        "total_scans": len(scans),
        "completed_scans": len(completed),
        "running_jobs": len([j for j in active_jobs.values() if j["status"] == "running"]),
        "recent_scans": scans[:20],
    }


@app.get("/scan-history")
def scan_history(limit: int = 20) -> list[dict[str, Any]]:
    return storage.recent_scans(limit=limit)


@app.get("/findings-by-target/{target}")
def findings_by_target(target: str) -> list[dict[str, Any]]:
    report_file = Path("reports") / f"{target}_report.json"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail="target report not found")
    data = json.loads(report_file.read_text(encoding="utf-8"))
    return data.get("findings", [])
