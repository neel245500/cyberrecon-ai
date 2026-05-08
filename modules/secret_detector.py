from __future__ import annotations

import re

from core.types import Severity
from modules.base import ModuleContext, ReconModule
from utils.helpers import simple_entropy


class SecretDetectorModule(ReconModule):
    name = "secret_detector"

    SECRET_PATTERNS = {
        "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "stripe": re.compile(r"sk_live_[0-9a-zA-Z]{24,}"),
        "github_token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
        "slack_token": re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
        "discord_token": re.compile(r"[MN][A-Za-z\d]{23}\.[\w-]{6}\.[\w-]{27}"),
        "jwt": re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"),
        "firebase": re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    }

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        js_path = f"{context.output_dir}/{target}_js_files.json"
        try:
            js_files = json.loads(open(js_path, "r", encoding="utf-8").read())
        except Exception:
            js_files = []

        leaks: list[dict] = []
        for js_url in js_files[:400]:
            try:
                response = await context.client.get(js_url, timeout=context.settings.timeout_seconds)
                body = response.text
                for secret_type, pattern in self.SECRET_PATTERNS.items():
                    for match in pattern.finditer(body):
                        value = match.group(0)
                        entropy = simple_entropy(value)
                        if entropy >= 3.2:
                            leaks.append(
                                {
                                    "type": secret_type,
                                    "value_preview": f"{value[:6]}...{value[-4:]}",
                                    "source": js_url,
                                    "entropy": round(entropy, 2),
                                }
                            )
            except Exception:
                continue

        findings = []
        if leaks:
            findings.append(
                self.finding(
                    title="Potential secret exposure",
                    description=f"Detected {len(leaks)} candidate secrets in JavaScript assets.",
                    severity=Severity.high,
                    endpoint=target,
                    evidence={"secrets": leaks[:50]},
                    score=8.4,
                )
            )

        return {"secrets": leaks, "findings": findings}
