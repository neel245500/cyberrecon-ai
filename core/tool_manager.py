from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

from core.constants import LINUX_TOOLS, MANDATORY_TOOLS, WINDOWS_TOOLS
from core.github_downloader import GitHubReleaseDownloader
from core.types import ToolStatus


@dataclass(slots=True)
class HostInfo:
    os_name: str
    arch: str
    is_windows: bool
    is_linux: bool


class ToolManager:
    def __init__(self, portable: bool = True, console: Console | None = None) -> None:
        self.portable = portable
        self.console = console or Console()
        self.host = self._detect_host()
        self.tools_dir = WINDOWS_TOOLS if self.host.is_windows else LINUX_TOOLS
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def _detect_host(self) -> HostInfo:
        os_name = platform.system().lower()
        arch = platform.machine().lower()
        return HostInfo(os_name=os_name, arch=arch, is_windows=os_name == "windows", is_linux=os_name == "linux")

    def _exe_name(self, tool: str) -> str:
        return f"{tool}.exe" if self.host.is_windows else tool

    def _tool_paths(self, tool: str) -> list[Path | str]:
        local_tool = self.tools_dir / self._exe_name(tool)
        return [local_tool, shutil.which(tool) or ""]

    def detect_tool(self, tool: str) -> ToolStatus:
        local_path, system_path = self._tool_paths(tool)
        if isinstance(local_path, Path) and local_path.exists():
            return ToolStatus(name=tool, found=True, source="portable", path=str(local_path), version=self._version_of(local_path))
        if system_path:
            return ToolStatus(name=tool, found=True, source="system", path=str(system_path), version=self._version_of(Path(system_path)))
        return ToolStatus(name=tool, found=False)

    def _version_of(self, path: Path) -> str | None:
        for flag in ["-version", "--version", "version"]:
            try:
                completed = subprocess.run([str(path), flag], capture_output=True, text=True, timeout=8)
                output = (completed.stdout or completed.stderr).strip()
                if output:
                    return output.splitlines()[0][:120]
            except Exception:
                continue
        return None

    async def install_tool(self, tool: str) -> ToolStatus:
        if tool not in MANDATORY_TOOLS:
            return ToolStatus(name=tool, found=False, error="Unsupported tool")

        status = self.detect_tool(tool)
        if status.found:
            return status

        if self.host.is_windows and await self._install_windows(tool):
            return self.detect_tool(tool)

        if self.host.is_linux and await self._install_linux(tool):
            return self.detect_tool(tool)

        return ToolStatus(name=tool, found=False, error="Automatic install failed")

    async def _install_windows(self, tool: str) -> bool:
        installers = [self._install_with_scoop, self._install_with_choco, self._install_with_go, self._install_with_github_release]
        for installer in installers:
            if await installer(tool):
                return True
        return False

    async def _install_linux(self, tool: str) -> bool:
        installers = [self._install_with_apt, self._install_with_go, self._install_with_github_release]
        for installer in installers:
            if await installer(tool):
                return True
        return False

    async def _run_shell(self, cmd: str) -> bool:
        try:
            completed = subprocess.run(cmd, shell=True, check=False, capture_output=True, text=True, timeout=180)
            return completed.returncode == 0
        except Exception:
            return False

    async def _install_with_scoop(self, tool: str) -> bool:
        if not self.host.is_windows or not shutil.which("scoop"):
            return False
        return await self._run_shell(f"scoop install {tool}")

    async def _install_with_choco(self, tool: str) -> bool:
        if not self.host.is_windows or not shutil.which("choco"):
            return False
        return await self._run_shell(f"choco install {tool} -y")

    async def _install_with_apt(self, tool: str) -> bool:
        if not self.host.is_linux or not shutil.which("apt"):
            return False
        return await self._run_shell(f"sudo apt-get update && sudo apt-get install -y {tool}")

    async def _install_with_go(self, tool: str) -> bool:
        if not shutil.which("go"):
            return False
        package = MANDATORY_TOOLS[tool].get("go")
        if not package:
            return False
        if not await self._run_shell(f"go install {package}"):
            return False

        gopath = Path.home() / "go" / "bin" / self._exe_name(tool)
        if gopath.exists():
            target = self.tools_dir / self._exe_name(tool)
            target.write_bytes(gopath.read_bytes())
            if not self.host.is_windows:
                target.chmod(0o755)
            return True
        return False

    async def _install_with_github_release(self, tool: str) -> bool:
        repo = MANDATORY_TOOLS[tool]["repo"]
        downloader = GitHubReleaseDownloader()
        try:
            release = await downloader.fetch_latest_release(repo)
            assets = release.get("assets", [])
            arch_tags = [self.host.arch, "amd64", "x86_64"]
            os_tags = ["windows"] if self.host.is_windows else ["linux"]
            candidate = None
            for asset in assets:
                name = asset.get("name", "").lower()
                if any(o in name for o in os_tags) and any(a in name for a in arch_tags):
                    candidate = asset
                    break
            if not candidate and assets:
                candidate = assets[0]
            if not candidate:
                return False

            tmp_download = self.tools_dir / candidate["name"]
            await downloader.download_asset(candidate["browser_download_url"], tmp_download)
            extracted = downloader.safe_extract(tmp_download, self.tools_dir / "_tmp")

            executable_name = self._exe_name(tool).lower()
            source_bin = next((p for p in extracted if p.name.lower() == executable_name), None)
            if source_bin is None:
                source_bin = next((p for p in extracted if executable_name in p.name.lower()), None)
            if source_bin is None:
                return False

            final_path = self.tools_dir / self._exe_name(tool)
            downloader.move_executable(source_bin, final_path, make_executable=not self.host.is_windows)
            return final_path.exists()
        except Exception as exc:
            import sys
            print(f"[ERROR] {tool} install failed: {exc}", file=sys.stderr)
            return False
        finally:
            await downloader.close()

    async def ensure_all_tools(self) -> list[ToolStatus]:
        statuses: list[ToolStatus] = []
        for tool in MANDATORY_TOOLS:
            status = await self.install_tool(tool)
            statuses.append(status)
        return statuses

    def tool_path(self, tool: str) -> str:
        status = self.detect_tool(tool)
        if status.found and status.path:
            return status.path
        return self._exe_name(tool)
