from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(str, Enum):
    info = "INFO"
    low = "LOW"
    medium = "MEDIUM"
    high = "HIGH"
    critical = "CRITICAL"


@dataclass(slots=True)
class Finding:
    module: str
    title: str
    description: str
    severity: Severity
    endpoint: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    ai_summary: str | None = None
    remediation: str | None = None


@dataclass(slots=True)
class TargetResult:
    target: str
    started_at: datetime
    ended_at: datetime | None = None
    findings: list[Finding] = field(default_factory=list)
    subdomains: set[str] = field(default_factory=set)
    live_hosts: list[dict[str, Any]] = field(default_factory=list)
    js_files: set[str] = field(default_factory=set)
    wayback_urls: set[str] = field(default_factory=set)


@dataclass(slots=True)
class ToolStatus:
    name: str
    found: bool
    version: str | None = None
    source: str | None = None
    path: str | None = None
    error: str | None = None
