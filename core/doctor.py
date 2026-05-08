from __future__ import annotations

import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

from rich.table import Table

from core.constants import PROJECT_ROOT
from core.tool_manager import ToolManager


def _check_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _check_playwright_browsers() -> bool:
    cache = Path.home() / ".cache" / "ms-playwright"
    if os.name == "nt":
        cache = Path.home() / "AppData" / "Local" / "ms-playwright"
    return cache.exists()


def _internet_ok() -> bool:
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False


def _can_write(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        test = path / ".write_test"
        test.write_text("ok", encoding="utf-8")
        test.unlink(missing_ok=True)
        return True
    except Exception:
        return False


def doctor_table(manager: ToolManager) -> Table:
    table = Table(title="CyberRecon Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Details")

    checks = [
        ("Python >=3.12", sys.version_info >= (3, 12), sys.version.split()[0]),
        ("Go", _check_cmd("go"), shutil.which("go") or "not found"),
        ("Node.js", _check_cmd("node"), shutil.which("node") or "not found"),
        ("Playwright browsers", _check_playwright_browsers(), "Installed" if _check_playwright_browsers() else "Missing"),
        ("Internet connectivity", _internet_ok(), "Reachable" if _internet_ok() else "Offline/blocked"),
        ("Write permissions", _can_write(PROJECT_ROOT / "output"), str(PROJECT_ROOT / "output")),
    ]

    for tool in ["subfinder", "amass", "assetfinder", "nuclei", "httpx", "waybackurls", "gau", "katana", "naabu"]:
        status = manager.detect_tool(tool)
        checks.append((f"Tool: {tool}", status.found, status.path or "not found"))

    for name, ok, details in checks:
        table.add_row(name, "PASS" if ok else "FAIL", details)

    return table


def install_playwright_if_missing() -> bool:
    if _check_playwright_browsers():
        return True
    try:
        completed = subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=False, timeout=300)
        return completed.returncode == 0
    except Exception:
        return False
