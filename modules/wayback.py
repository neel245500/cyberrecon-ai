from __future__ import annotations

from core.types import Severity
from modules.base import ModuleContext, ReconModule


class WaybackModule(ReconModule):
    name = "wayback"

    async def run(self, target: str, context: ModuleContext) -> dict:
        urls: set[str] = set()
        for provider in [
            f"https://web.archive.org/cdx/search/cdx?url=*.{target}/*&output=text&fl=original",
            f"https://index.commoncrawl.org/CC-MAIN-2024-10-index?url=*.{target}/*&output=text",
        ]:
            try:
                response = await context.client.get(provider, timeout=35)
                if response.status_code == 200:
                    urls.update(line.strip() for line in response.text.splitlines() if line.strip().startswith("http"))
            except Exception:
                continue

        params = sorted({u for u in urls if "?" in u})
        archived_js = sorted({u for u in urls if ".js" in u.lower()})

        findings = []
        if len(params) > 100:
            findings.append(
                self.finding(
                    title="Large historical parameter surface",
                    description=f"Discovered {len(params)} archived parameterized URLs.",
                    severity=Severity.medium,
                    endpoint=target,
                    evidence={"sample": params[:30]},
                    score=6.1,
                )
            )

        return {"wayback_urls": sorted(urls), "params": params, "archived_js": archived_js, "findings": findings}
