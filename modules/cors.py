from __future__ import annotations

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class CorsModule(ReconModule):
    name = "cors"

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        try:
            live_hosts = json.loads(open(f"{context.output_dir}/{target}_live_hosts.json", "r", encoding="utf-8").read())
        except Exception:
            live_hosts = []

        issues: list[dict] = []
        test_origin = "https://evil.example"

        for host in live_hosts[:300]:
            url = host.get("url")
            if not url:
                continue
            try:
                response = await context.client.get(url, headers={"Origin": test_origin}, timeout=context.settings.timeout_seconds)
            except Exception:
                continue

            aco = response.headers.get("Access-Control-Allow-Origin", "")
            acc = response.headers.get("Access-Control-Allow-Credentials", "")

            if aco == "*" and acc.lower() == "true":
                issues.append({"url": url, "issue": "Wildcard origin with credentials", "severity": "high"})
            elif aco == test_origin:
                issues.append({"url": url, "issue": "Origin reflection", "severity": "medium"})

        findings = []
        for issue in issues:
            findings.append(
                self.finding(
                    title="Potential CORS misconfiguration",
                    description=issue["issue"],
                    severity=Severity.high if issue["severity"] == "high" else Severity.medium,
                    endpoint=issue["url"],
                    evidence=issue,
                    score=8.1 if issue["severity"] == "high" else 6.2,
                )
            )

        return {"cors_issues": issues, "findings": findings}
