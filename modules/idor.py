from __future__ import annotations

import re

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class IdorModule(ReconModule):
    name = "idor"

    NUMERIC_ID_RE = re.compile(r"/(?:user|account|order|invoice|profile|doc|api)/\d+", re.IGNORECASE)
    UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}")

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        try:
            endpoints = json.loads(open(f"{context.output_dir}/{target}_js_endpoints.json", "r", encoding="utf-8").read())
        except Exception:
            endpoints = []

        suspicious: list[dict] = []
        for endpoint in endpoints:
            if self.NUMERIC_ID_RE.search(endpoint):
                suspicious.append({"endpoint": endpoint, "pattern": "numeric_object_reference", "score": 0.7})
            if self.UUID_RE.search(endpoint):
                suspicious.append({"endpoint": endpoint, "pattern": "uuid_object_reference", "score": 0.5})

        findings = [
            self.finding(
                title="Potential IDOR pattern",
                description=f"Endpoint includes {item['pattern'].replace('_', ' ')}.",
                severity=Severity.medium,
                endpoint=item["endpoint"],
                evidence=item,
                score=6.0,
            )
            for item in suspicious[:120]
        ]

        return {"idor_candidates": suspicious, "findings": findings}
