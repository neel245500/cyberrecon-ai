from __future__ import annotations

from pathlib import Path

from playwright.async_api import async_playwright

from modules.base import ModuleContext, ReconModule


class ScreenshotModule(ReconModule):
    name = "screenshots"

    async def run(self, target: str, context: ModuleContext) -> dict:
        import json

        try:
            live_hosts = json.loads(open(f"{context.output_dir}/{target}_live_hosts.json", "r", encoding="utf-8").read())
        except Exception:
            live_hosts = []

        out_dir = Path(context.output_dir) / "screenshots" / target
        out_dir.mkdir(parents=True, exist_ok=True)

        shots: list[dict] = []
        login_candidates: list[str] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": 1440, "height": 900})
            for host in live_hosts[:80]:
                url = host.get("url")
                if not url:
                    continue
                try:
                    await page.goto(url, timeout=20000)
                    content = (await page.content()).lower()
                    file_name = f"{host['host'].replace('.', '_')}.png"
                    file_path = out_dir / file_name
                    await page.screenshot(path=str(file_path), full_page=True)
                    shots.append({"url": url, "path": str(file_path)})
                    if "password" in content and ("login" in content or "sign in" in content):
                        login_candidates.append(url)
                except Exception:
                    continue
            await browser.close()

        return {"screenshots": shots, "login_pages": sorted(set(login_candidates)), "findings": []}
