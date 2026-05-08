from __future__ import annotations

import hashlib
import shutil
import stat
import tarfile
import zipfile
from pathlib import Path

import httpx


class GitHubReleaseDownloader:
    def __init__(self, token: str | None = None) -> None:
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "CyberReconAI"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self.client = httpx.AsyncClient(timeout=30, headers=headers, follow_redirects=True)

    async def close(self) -> None:
        await self.client.aclose()

    async def fetch_latest_release(self, repo: str) -> dict:
        response = await self.client.get(f"https://api.github.com/repos/{repo}/releases/latest")
        response.raise_for_status()
        return response.json()

    async def download_asset(self, url: str, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        async with self.client.stream("GET", url) as response:
            response.raise_for_status()
            with destination.open("wb") as handle:
                async for chunk in response.aiter_bytes():
                    handle.write(chunk)
        return destination

    def verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        return digest.lower() == expected_sha256.lower()

    def safe_extract(self, archive_path: Path, output_dir: Path) -> list[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        extracted: list[Path] = []

        if archive_path.suffix == ".zip":
            with zipfile.ZipFile(archive_path) as zf:
                for member in zf.namelist():
                    target_path = (output_dir / member).resolve()
                    if not str(target_path).startswith(str(output_dir.resolve())):
                        raise ValueError("Unsafe path in archive")
                zf.extractall(output_dir)
                extracted = [output_dir / name for name in zf.namelist()]
        elif archive_path.suffixes[-2:] == [".tar", ".gz"] or archive_path.suffix == ".tgz":
            with tarfile.open(archive_path, "r:gz") as tf:
                for member in tf.getmembers():
                    target_path = (output_dir / member.name).resolve()
                    if not str(target_path).startswith(str(output_dir.resolve())):
                        raise ValueError("Unsafe path in archive")
                tf.extractall(output_dir)
                extracted = [output_dir / m.name for m in tf.getmembers()]
        else:
            extracted = [archive_path]

        return extracted

    def move_executable(self, source: Path, destination: Path, make_executable: bool = True) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        if make_executable and destination.exists():
            mode = destination.stat().st_mode
            destination.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        return destination
