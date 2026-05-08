from __future__ import annotations

import re

from core.types import Severity
from modules.base import ModuleContext, ReconModule
from utils.helpers import ENDPOINT_RE


class JavaScriptAnalyzerModule(ReconModule):
    name = "js_analyzer"

    JS_RE = re.compile(r"https?://[^\"'\s>]+\.js(?:\?[^\"'\s>]*)?", re.IGNORECASE)

    async def run(self, target: str, context: ModuleContext) -> dict:
        input_file = f"{context.output_dir}/{target}_live_hosts.json"
        try:
            import json

            with open(input_file, "r", encoding="utf-8") as handle:
                live_hosts = json.load(handle)
        except Exception:
            live_hosts = [{"url": f"https://{target}"}]

        js_urls: set[str] = set()
        endpoints: set[str] = set()
        source_maps: set[str] = set()

        for host in live_hosts:
            url = host.get("url")
            if not url:
                continue
            try:
                response = await context.client.get(url, timeout=context.settings.timeout_seconds)
                js_urls.update(self.JS_RE.findall(response.text))
                for js in js_urls:
                    if js.endswith(".map"):
                        source_maps.add(js)
            except Exception:
                continue

        for js_url in list(js_urls)[:300]:
            try:
                response = await context.client.get(js_url, timeout=context.settings.timeout_seconds)
                endpoints.update(match.group(0) for match in ENDPOINT_RE.finditer(response.text))
            except Exception:
                continue

        findings = []
        if source_maps:
            findings.append(
                self.finding(
                    title="Source maps exposed",
                    description="Public JavaScript source maps may leak sensitive implementation details.",
                    severity=Severity.medium,
                    endpoint=target,
                    evidence={"sources": sorted(source_maps)},
                    score=5.5,
                )
            )

        return {
            "js_files": sorted(js_urls),
            "endpoints": sorted(endpoints),
            "findings": findings,
        }
