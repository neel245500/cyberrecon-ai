from __future__ import annotations

import asyncio

from core.types import Severity
from modules.base import ModuleContext, ReconModule
from utils.helpers import favicon_hash


class LiveHostModule(ReconModule):
    name = "live_hosts"

    async def _probe(self, host: str, context: ModuleContext) -> dict | None:
        for scheme in ["https", "http"]:
            url = f"{scheme}://{host}"
            try:
                response = await context.client.get(url, follow_redirects=True, timeout=context.settings.timeout_seconds)
                title = ""
                if "<title" in response.text.lower():
                    title = response.text.lower().split("<title", 1)[1].split(">", 1)[-1].split("</title>", 1)[0].strip()[:120]
                favicon = None
                try:
                    icon = await context.client.get(f"{url}/favicon.ico", timeout=6)
                    if icon.status_code == 200 and icon.content:
                        favicon = favicon_hash(icon.content)
                except Exception:
                    pass

                return {
                    "host": host,
                    "url": str(response.url),
                    "status": response.status_code,
                    "title": title,
                    "favicon_hash": favicon,
                    "length": len(response.text),
                }
            except Exception:
                continue
        return None

    async def run(self, target: str, context: ModuleContext) -> dict:
        input_file = f"{context.output_dir}/{target}_subdomains.txt"
        try:
            with open(input_file, "r", encoding="utf-8") as handle:
                hosts = [line.strip() for line in handle if line.strip()]
        except FileNotFoundError:
            hosts = [target]

        sem = asyncio.Semaphore(context.settings.concurrency)

        async def bounded_probe(host: str) -> dict | None:
            async with sem:
                return await self._probe(host, context)

        results = [r for r in await asyncio.gather(*(bounded_probe(h) for h in hosts), return_exceptions=False) if r]

        findings = []
        if any(r["status"] >= 500 for r in results):
            findings.append(
                self.finding(
                    title="Hosts with server errors",
                    description="One or more live hosts returned 5xx responses.",
                    severity=Severity.low,
                    endpoint=target,
                    evidence={"sample": [r for r in results if r["status"] >= 500][:10]},
                    score=2.5,
                )
            )

        return {"live_hosts": results, "findings": findings}
