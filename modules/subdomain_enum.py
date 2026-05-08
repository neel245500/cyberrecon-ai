from __future__ import annotations

import json
from pathlib import Path

from core.types import Severity
from modules.base import ModuleContext, ReconModule
from utils.async_runner import run_command


class SubdomainEnumModule(ReconModule):
    name = "subdomain_enum"

    async def run(self, target: str, context: ModuleContext) -> dict:
        output_file = Path(context.output_dir) / f"{target}_subdomains.txt"
        tools = ["subfinder", "amass", "assetfinder"]
        found: set[str] = set()

        for tool in tools:
            command = [context.tool_manager.tool_path(tool), "-d", target]
            if tool == "amass":
                command = [context.tool_manager.tool_path(tool), "enum", "-passive", "-d", target]
            result = await run_command(command, timeout=240)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    line = line.strip().lower()
                    if line and line.endswith(target):
                        found.add(line)

        crt_response = await context.client.get(f"https://crt.sh/?q=%25.{target}&output=json")
        if crt_response.status_code == 200:
            try:
                data = crt_response.json()
                for row in data:
                    names = row.get("name_value", "").split("\n")
                    for name in names:
                        name = name.strip().lower()
                        if name and name.endswith(target):
                            found.add(name)
            except json.JSONDecodeError:
                pass

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(sorted(found)), encoding="utf-8")

        findings = []
        if len(found) > 500:
            findings.append(
                self.finding(
                    title="Large attack surface",
                    description=f"Discovered {len(found)} subdomains.",
                    severity=Severity.medium,
                    endpoint=target,
                    evidence={"subdomain_count": len(found)},
                    score=4.8,
                )
            )

        return {"subdomains": sorted(found), "findings": findings}
