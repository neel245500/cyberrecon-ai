from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from jinja2 import Template

from core.constants import REPORTS_ROOT
from core.types import Finding, TargetResult


HTML_TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>CyberRecon AI Report</title>
  <style>
    body { font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #f6f8fa; }
    h1 { color: #0f172a; }
    .card { background: white; border-radius: 12px; padding: 14px; margin-bottom: 10px; }
    .sev-CRITICAL { border-left: 6px solid #b91c1c; }
    .sev-HIGH { border-left: 6px solid #dc2626; }
    .sev-MEDIUM { border-left: 6px solid #d97706; }
    .sev-LOW { border-left: 6px solid #65a30d; }
    .sev-INFO { border-left: 6px solid #2563eb; }
    code { background: #eef2ff; padding: 2px 6px; border-radius: 6px; }
  </style>
</head>
<body>
  <h1>CyberRecon AI Report - {{ target }}</h1>
  <p>Generated at {{ generated_at }}</p>
  {% for finding in findings %}
  <div class=\"card sev-{{ finding.severity }}\">
    <h3>{{ finding.title }} ({{ finding.severity }})</h3>
    <p>{{ finding.description }}</p>
    <p><strong>Endpoint:</strong> <code>{{ finding.endpoint or 'N/A' }}</code></p>
    <p><strong>Score:</strong> {{ finding.score }}</p>
    <p><strong>AI Summary:</strong> {{ finding.ai_summary or 'N/A' }}</p>
    <p><strong>Remediation:</strong> {{ finding.remediation or 'N/A' }}</p>
  </div>
  {% endfor %}
</body>
</html>
"""


def save_json_report(result: TargetResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{result.target}_report.json"
    payload = {
        "target": result.target,
        "started_at": result.started_at.isoformat(),
        "ended_at": (result.ended_at or datetime.utcnow()).isoformat(),
        "findings": [asdict(f) for f in result.findings],
        "counts": {
            "subdomains": len(result.subdomains),
            "live_hosts": len(result.live_hosts),
            "js_files": len(result.js_files),
            "wayback_urls": len(result.wayback_urls),
        },
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return report_path


def save_markdown_report(result: TargetResult, output_dir: Path, ai_summary: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{result.target}_report.md"

    lines = [
        f"# CyberRecon AI Report - {result.target}",
        "",
        f"- Started: {result.started_at.isoformat()}",
        f"- Ended: {(result.ended_at or datetime.utcnow()).isoformat()}",
        f"- Subdomains: {len(result.subdomains)}",
        f"- Live hosts: {len(result.live_hosts)}",
        f"- JS files: {len(result.js_files)}",
        f"- Historical URLs: {len(result.wayback_urls)}",
        "",
        "## AI Executive Summary",
        ai_summary,
        "",
        "## Findings",
    ]

    for finding in result.findings:
        lines.extend(
            [
                f"### [{finding.severity.value}] {finding.title}",
                f"- Module: {finding.module}",
                f"- Endpoint: {finding.endpoint or 'N/A'}",
                f"- Score: {finding.score}",
                f"- Description: {finding.description}",
                f"- Remediation: {finding.remediation or 'N/A'}",
                "",
            ]
        )

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def save_html_report(result: TargetResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"{result.target}_report.html"
    rendered = Template(HTML_TEMPLATE).render(
        target=result.target,
        generated_at=datetime.utcnow().isoformat(),
        findings=[
            {
                "title": f.title,
                "description": f.description,
                "severity": f.severity.value,
                "endpoint": f.endpoint,
                "score": round(f.score, 2),
                "ai_summary": f.ai_summary,
                "remediation": f.remediation,
            }
            for f in result.findings
        ],
    )
    report_path.write_text(rendered, encoding="utf-8")
    return report_path


def save_all_reports(result: TargetResult, ai_summary: str) -> dict[str, Path]:
    REPORTS_ROOT.mkdir(parents=True, exist_ok=True)
    return {
        "json": save_json_report(result, REPORTS_ROOT),
        "markdown": save_markdown_report(result, REPORTS_ROOT, ai_summary),
        "html": save_html_report(result, REPORTS_ROOT),
    }
