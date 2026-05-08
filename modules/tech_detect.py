from __future__ import annotations

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class TechDetectModule(ReconModule):
    name = "tech_detect"

    SIGNATURES = {
        "cloudflare": ["cf-ray", "cloudflare"],
        "nginx": ["nginx"],
        "apache": ["apache"],
        "nextjs": ["next.js", "__next"],
        "react": ["react", "data-reactroot"],
        "wordpress": ["wp-content", "wp-includes"],
        "laravel": ["laravel_session"],
    }

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        try:
            live_hosts = json.loads(open(f"{context.output_dir}/{target}_live_hosts.json", "r", encoding="utf-8").read())
        except Exception:
            live_hosts = []

        inventory: dict[str, set[str]] = {}

        for host in live_hosts[:300]:
            url = host.get("url")
            if not url:
                continue
            try:
                response = await context.client.get(url, timeout=context.settings.timeout_seconds)
                haystack = " ".join([str(response.headers), response.text[:5000]]).lower()
                for tech, signatures in self.SIGNATURES.items():
                    if any(sig in haystack for sig in signatures):
                        inventory.setdefault(tech, set()).add(url)
            except Exception:
                continue

        findings = []
        if "wordpress" in inventory:
            findings.append(
                self.finding(
                    title="WordPress surface detected",
                    description="WordPress markers found on one or more hosts.",
                    severity=Severity.low,
                    endpoint=target,
                    evidence={"hosts": sorted(inventory["wordpress"])[:20]},
                    score=3.2,
                )
            )

        return {"technologies": {k: sorted(v) for k, v in inventory.items()}, "findings": findings}
