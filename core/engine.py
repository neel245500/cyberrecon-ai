from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import httpx
from rich.console import Console

from ai.analyzer import AiAnalyzer
from core.config import Config
from core.constants import OUTPUT_ROOT, PROJECT_ROOT
from core.reporting import save_all_reports
from core.storage import Storage
from core.tool_manager import ToolManager
from core.types import Finding, TargetResult
from modules.base import ModuleContext
from modules.cors import CorsModule
from modules.idor import IdorModule
from modules.js_analyzer import JavaScriptAnalyzerModule
from modules.live_hosts import LiveHostModule
from modules.screenshots import ScreenshotModule
from modules.secret_detector import SecretDetectorModule
from modules.ssrf import SsrfModule
from modules.subdomain_enum import SubdomainEnumModule
from modules.tech_detect import TechDetectModule
from modules.wayback import WaybackModule
from plugins.manager import ModuleRegistry, PluginManager


console = Console()


class ScanEngine:
    def __init__(self, portable: bool = True) -> None:
        self.config = Config()
        self.settings = self.config.load()
        self.tool_manager = ToolManager(portable=portable)
        self.storage = Storage()
        self.ai = AiAnalyzer(self.settings)

    async def install_tools(self) -> list:
        return await self.tool_manager.ensure_all_tools()

    def registry(self, full: bool = True) -> ModuleRegistry:
        registry = ModuleRegistry()
        base_modules = [
            SubdomainEnumModule(),
            LiveHostModule(),
            JavaScriptAnalyzerModule(),
            SecretDetectorModule(),
            WaybackModule(),
            TechDetectModule(),
            CorsModule(),
            SsrfModule(),
            IdorModule(),
        ]
        if full:
            base_modules.append(ScreenshotModule())

        registry.register(base_modules)
        plugin_manager = PluginManager(PROJECT_ROOT / "plugins")
        registry.register(plugin_manager.load_modules())
        return registry

    async def scan(self, target: str, full: bool = False) -> dict:
        output_dir = OUTPUT_ROOT / target
        output_dir.mkdir(parents=True, exist_ok=True)

        scan_id = self.storage.create_scan(target)
        result = TargetResult(target=target, started_at=datetime.utcnow())

        console.print(f"[cyan][+][/cyan] Scan ID: {scan_id}")
        console.print(f"[cyan][+][/cyan] Target: {target}")
        console.print(f"[cyan][+][/cyan] Output directory: {output_dir}")
        console.print()

        async with httpx.AsyncClient(
            verify=False,
            headers={"User-Agent": self.settings.user_agent},
            follow_redirects=True,
            timeout=self.settings.timeout_seconds,
        ) as client:
            context = ModuleContext(
                settings=self.settings,
                tool_manager=self.tool_manager,
                client=client,
                output_dir=str(output_dir),
            )

            registry = self.registry(full=full)
            findings: list[Finding] = []
            module_count = len(registry.get_all())

            for idx, module in enumerate(registry.get_all(), 1):
                console.print(f"[yellow][*][/yellow] [{idx}/{module_count}] Running {module.name}...")
                try:
                    module_result = await module.run(target, context)
                    console.print(f"[green][✓][/green] {module.name} completed")

                    if "subdomains" in module_result:
                        result.subdomains.update(module_result["subdomains"])
                        (output_dir / f"{target}_subdomains.txt").write_text("\n".join(sorted(result.subdomains)), encoding="utf-8")
                        console.print(f"  → Found {len(result.subdomains)} subdomains")

                    if "live_hosts" in module_result:
                        result.live_hosts = module_result["live_hosts"]
                        (output_dir / f"{target}_live_hosts.json").write_text(json.dumps(result.live_hosts, indent=2), encoding="utf-8")
                        console.print(f"  → Found {len(result.live_hosts)} live hosts")

                    if "js_files" in module_result:
                        result.js_files.update(module_result["js_files"])
                        (output_dir / f"{target}_js_files.json").write_text(json.dumps(sorted(result.js_files), indent=2), encoding="utf-8")
                        console.print(f"  → Found {len(result.js_files)} JS files")

                    if "endpoints" in module_result:
                        endpoints_count = len(module_result["endpoints"])
                        (output_dir / f"{target}_js_endpoints.json").write_text(json.dumps(module_result["endpoints"], indent=2), encoding="utf-8")
                        console.print(f"  → Extracted {endpoints_count} endpoints")

                    if "wayback_urls" in module_result:
                        result.wayback_urls.update(module_result["wayback_urls"])
                        (output_dir / f"{target}_wayback_urls.json").write_text(json.dumps(sorted(result.wayback_urls), indent=2), encoding="utf-8")
                        console.print(f"  → Found {len(result.wayback_urls)} historical URLs")

                    if "findings" in module_result:
                        findings.extend(module_result["findings"])
                        if module_result["findings"]:
                            console.print(f"  → [red]{len(module_result['findings'])} findings[/red]")

                except Exception as exc:
                    console.print(f"[red][!][/red] {module.name} error: {exc}")
                    continue

            console.print()
            console.print(f"[cyan][+][/cyan] Prioritizing findings...")
            findings = await self.ai.prioritize(findings)
            for finding in findings:
                self.ai.annotate_remediation(finding)

            console.print(f"[cyan][+][/cyan] Generating AI summary...")
            ai_summary = await self.ai.get_summary(findings)
            for finding in findings:
                finding.ai_summary = ai_summary

            result.findings = findings
            result.ended_at = datetime.utcnow()

            console.print(f"[cyan][+][/cyan] Saving reports...")
            reports = save_all_reports(result, ai_summary)
            summary = f"{len(findings)} findings across {len(result.live_hosts)} live hosts."
            self.storage.complete_scan(scan_id, summary)

            for finding in result.findings:
                self.storage.add_finding(scan_id, asdict(finding))

            console.print()
            console.print(f"[green][✓][/green] Scan completed!")
            console.print(f"[yellow]Summary:[/yellow] {summary}")

            return {
                "scan_id": scan_id,
                "target": target,
                "summary": summary,
                "reports": {k: str(v) for k, v in reports.items()},
                "findings": [asdict(f) for f in result.findings],
            }
