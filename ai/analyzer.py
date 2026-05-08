from __future__ import annotations

import json

import httpx

from core.config import Settings
from core.types import Finding, Severity


class AiAnalyzer:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def prioritize(self, findings: list[Finding]) -> list[Finding]:
        for finding in findings:
            if finding.severity == Severity.critical:
                finding.score = max(finding.score, 9.0)
            elif finding.severity == Severity.high:
                finding.score = max(finding.score, 7.5)
            elif finding.severity == Severity.medium:
                finding.score = max(finding.score, 5.0)
            elif finding.severity == Severity.low:
                finding.score = max(finding.score, 3.0)
            else:
                finding.score = max(finding.score, 1.0)

        findings.sort(key=lambda f: f.score, reverse=True)
        return findings

    async def summarize_with_openai(self, findings: list[Finding]) -> str:
        if not self.settings.openai_api_key:
            return "OpenAI API key not configured"
        
        payload = {
            "model": "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a cybersecurity analyst. Provide concise vulnerability summaries.",
                }
            ] + [
                {
                    "role": "user",
                    "content": self._build_prompt(findings),
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500,
        }
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except Exception as exc:
            return f"AI summary failed: {str(exc)}"

    async def summarize_with_ollama(self, findings: list[Finding]) -> str:
        payload = {
            "model": self.settings.ollama_model,
            "prompt": self._build_prompt(findings),
            "stream": False,
        }
        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(f"{self.settings.ollama_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "AI summary unavailable")
        except Exception:
            return "AI summary unavailable. Ensure Ollama is running with the configured model."

    async def get_summary(self, findings: list[Finding]) -> str:
        """Use OpenAI if available and configured, otherwise fall back to Ollama"""
        if self.settings.openai_enabled and self.settings.openai_api_key:
            return await self.summarize_with_openai(findings)
        return await self.summarize_with_ollama(findings)

    def annotate_remediation(self, finding: Finding) -> None:
        if "cors" in finding.module:
            finding.remediation = "Restrict Access-Control-Allow-Origin to trusted origins and disable credentials for wildcard policies."
        elif "secret" in finding.module:
            finding.remediation = "Revoke exposed tokens immediately, rotate credentials, and move secrets to server-side storage."
        elif "idor" in finding.module:
            finding.remediation = "Enforce object-level authorization checks and avoid predictable identifiers in direct object references."
        elif "ssrf" in finding.module:
            finding.remediation = "Use strict allowlists for outbound fetch destinations and block internal metadata/IP ranges."
        else:
            finding.remediation = "Validate security controls, reduce exposed surface area, and enforce least privilege."

    def _build_prompt(self, findings: list[Finding]) -> str:
        serialized = [
            {
                "module": f.module,
                "title": f.title,
                "severity": f.severity.value,
                "endpoint": f.endpoint,
                "description": f.description,
            }
            for f in findings[:25]
        ]
        return (
            "You are a security analyst. Summarize top vulnerabilities, business impact, and remediation priorities. "
            "Keep it concise and professional. Findings JSON: "
            + json.dumps(serialized)
        )
