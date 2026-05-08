from __future__ import annotations

import asyncio
import json
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from core.doctor import doctor_table, install_playwright_if_missing
from core.engine import ScanEngine
from core.tool_manager import ToolManager
import os

app = typer.Typer(help="CyberRecon AI - AI-powered bug bounty reconnaissance framework", add_completion=False)
console = Console()


def banner() -> None:
    console.print(
        Panel.fit(
            "[bold cyan]CYBERRECON AI[/bold cyan]\n[white]AI-Powered Recon Framework[/white]\n[dim]Authorized testing only[/dim]",
            border_style="cyan",
        )
    )


def legal_gate() -> None:
    console.print(
        "[bold yellow]Legal Warning:[/bold yellow] Use this tool only for authorized penetration testing, bug bounty reconnaissance, and approved research environments."
    )
    confirmation = typer.prompt("Type exactly: I confirm I have authorization to scan this target")
    if confirmation.strip() != "I confirm I have authorization to scan this target":
        console.print("[bold red]Authorization confirmation failed. Aborting.[/bold red]")
        raise typer.Exit(code=1)


@app.command()
def install(portable: bool = typer.Option(True, help="Install tools to local tools directory")) -> None:
    banner()
    engine = ScanEngine(portable=portable)

    async def _run() -> None:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(description="Installing and verifying mandatory tools...", total=None)
            statuses = await engine.install_tools()
            progress.remove_task(task)

        table = Table(title="Tool Installation Status", box=box.SIMPLE_HEAVY)
        table.add_column("Tool")
        table.add_column("Installed")
        table.add_column("Source")
        table.add_column("Path")
        for status in statuses:
            table.add_row(status.name, "Yes" if status.found else "No", status.source or "n/a", status.path or "n/a")
        console.print(table)

        if install_playwright_if_missing():
            console.print("[green]Playwright browsers ready.[/green]")
        else:
            console.print("[yellow]Playwright browser install failed. Run: playwright install chromium[/yellow]")

    asyncio.run(_run())


@app.command()
def doctor() -> None:
    banner()
    manager = ToolManager(portable=True)
    console.print(doctor_table(manager))


@app.command("update-tools")
def update_tools() -> None:
    banner()
    engine = ScanEngine(portable=True)

    async def _run() -> None:
        statuses = await engine.install_tools()
        updated = sum(1 for s in statuses if s.found)
        console.print(f"[green]Tool refresh completed. {updated}/{len(statuses)} tools ready.[/green]")

    asyncio.run(_run())


@app.command()
def verify() -> None:
    banner()
    manager = ToolManager(portable=True)

    table = Table(title="Verification", box=box.MINIMAL_DOUBLE_HEAD)
    table.add_column("Tool")
    table.add_column("Status")
    table.add_column("Version")
    for tool in ["subfinder", "amass", "assetfinder", "nuclei", "httpx", "waybackurls", "gau", "katana", "naabu"]:
        status = manager.detect_tool(tool)
        table.add_row(tool, "OK" if status.found else "Missing", status.version or "n/a")
    console.print(table)


@app.command()
def scan(target: str, full: bool = typer.Option(False, help="Enable full mode including screenshots")) -> None:
    banner()
    legal_gate()
    engine = ScanEngine(portable=True)

    async def _run() -> None:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(description=f"Scanning {target}...", total=None)
            result = await engine.scan(target, full=full)
            progress.remove_task(task)

        findings = result.get("findings", [])
        table = Table(title="Findings Summary", box=box.ROUNDED)
        table.add_column("Severity")
        table.add_column("Title")
        table.add_column("Module")
        table.add_column("Score")

        for finding in findings[:20]:
            table.add_row(finding["severity"], finding["title"], finding["module"], str(round(finding["score"], 2)))

        console.print(table)
        console.print(Panel.fit(f"Reports generated:\n{json.dumps(result['reports'], indent=2)}", title="Artifacts"))

    asyncio.run(_run())


@app.command()
def recon(target: str) -> None:
    scan(target=target, full=False)


@app.command()
def js(target: str) -> None:
    output_file = Path("output") / target / f"{target}_js_endpoints.json"
    if not output_file.exists():
        console.print("[yellow]No JS endpoint output found. Run a scan first.[/yellow]")
        raise typer.Exit(code=1)
    endpoints = json.loads(output_file.read_text(encoding="utf-8"))
    table = Table(title=f"JavaScript Endpoints - {target}")
    table.add_column("Endpoint")
    for endpoint in endpoints[:300]:
        table.add_row(endpoint)
    console.print(table)


@app.command()
def secrets(target: str) -> None:
    scan_file = Path("reports") / f"{target}_report.json"
    if not scan_file.exists():
        console.print("[yellow]No report found. Run a scan first.[/yellow]")
        raise typer.Exit(code=1)

    data = json.loads(scan_file.read_text(encoding="utf-8"))
    findings = [f for f in data.get("findings", []) if f.get("module") == "secret_detector"]
    console.print_json(json.dumps(findings, indent=2))


@app.command()
def cors(target: str) -> None:
    scan_file = Path("reports") / f"{target}_report.json"
    if not scan_file.exists():
        console.print("[yellow]No report found. Run a scan first.[/yellow]")
        raise typer.Exit(code=1)

    data = json.loads(scan_file.read_text(encoding="utf-8"))
    findings = [f for f in data.get("findings", []) if f.get("module") == "cors"]
    console.print_json(json.dumps(findings, indent=2))


@app.command()
def screenshots(target: str) -> None:
    dir_path = Path("output") / target / "screenshots" / target
    if not dir_path.exists():
        console.print("[yellow]No screenshots found. Run scan --full first.[/yellow]")
        raise typer.Exit(code=1)

    table = Table(title=f"Screenshots - {target}")
    table.add_column("File")
    for file in sorted(dir_path.glob("*.png")):
        table.add_row(str(file))
    console.print(table)


@app.command()
def configure() -> None:
    """Interactive one-time configuration for API keys (writes to .env)."""
    banner()
    env_file = Path(".env")
    # Ensure .env exists
    if not env_file.exists():
        env_file.write_text("# CyberRecon AI environment overrides\n")

    console.print("[cyan]Configure API keys (these are stored in .env and should not be committed).[/cyan]")
    # OpenAI key
    set_openai = typer.confirm("Do you want to add/update your OpenAI (ChatGPT) API key?")
    if set_openai:
        key = typer.prompt("Paste your OpenAI API key (starts with sk-)", hide_input=True)
        content = env_file.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if not l.strip().startswith("OPENAI_API_KEY=")]
        lines.append(f"OPENAI_API_KEY={key}")
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.print("[green]OpenAI API key saved to .env (do not commit this file).[/green]")

    # Optional: Ollama URL
    set_ollama = typer.confirm("Do you want to change Ollama URL/model settings?")
    if set_ollama:
        ollama_url = typer.prompt("Ollama URL", default=os.getenv("OLLAMA_URL", "http://localhost:11434"))
        ollama_model = typer.prompt("Ollama model", default=os.getenv("OLLAMA_MODEL", "llama3"))
        content = env_file.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if not l.strip().startswith("OLLAMA_URL=") and not l.strip().startswith("OLLAMA_MODEL=")]
        lines.append(f"OLLAMA_URL={ollama_url}")
        lines.append(f"OLLAMA_MODEL={ollama_model}")
        env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        console.print("[green]Ollama settings updated in .env.[/green]")

    console.print(Panel.fit("Configuration complete. Remember: never commit `.env` to a public repo.", title="Secure Reminder"))


if __name__ == "__main__":
    app()
