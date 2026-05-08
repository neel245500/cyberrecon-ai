from __future__ import annotations

import re

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class SsrfModule(ReconModule):
    name = "ssrf"

    PARAM_RE = re.compile(r"[?&](?:url|uri|redirect|next|dest|callback|return|image|feed|target)=", re.IGNORECASE)

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        try:
            wayback_urls = json.loads(open(f"{context.output_dir}/{target}_wayback_urls.json", "r", encoding="utf-8").read())
        except Exception:
            wayback_urls = []

        candidates = [u for u in wayback_urls if self.PARAM_RE.search(u)]

        findings = [
            self.finding(
                title="Potential SSRF parameter",
                description="URL contains a parameter name frequently associated with server-side fetching.",
                severity=Severity.medium,
                endpoint=url,
                evidence={"parameterized_url": url},
                score=5.9,
            )
            for url in candidates[:150]
        ]

        return {"ssrf_candidates": candidates, "findings": findings}
