from __future__ import annotations

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class SecurityHeadersPlugin(ReconModule):
    name = "plugin_security_headers"

    async def run(self, target: str, context: ModuleContext) -> dict:
        findings = []
        try:
            response = await context.client.get(f"https://{target}", timeout=context.settings.timeout_seconds)
            headers = response.headers
            missing = [h for h in ["Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options"] if h not in headers]
            if missing:
                findings.append(
                    self.finding(
                        title="Missing security headers",
                        description="One or more recommended security headers are missing.",
                        severity=Severity.low,
                        endpoint=f"https://{target}",
                        evidence={"missing_headers": missing},
                        score=2.8,
                    )
                )
        except Exception:
            pass

        return {"findings": findings}


PLUGIN_MODULES = [SecurityHeadersPlugin()]
