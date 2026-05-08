from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_ROOT = PROJECT_ROOT / "tools"
WINDOWS_TOOLS = TOOLS_ROOT / "windows"
LINUX_TOOLS = TOOLS_ROOT / "linux"
OUTPUT_ROOT = PROJECT_ROOT / "output"
REPORTS_ROOT = PROJECT_ROOT / "reports"
SCREENSHOTS_ROOT = PROJECT_ROOT / "screenshots"
LOGS_ROOT = PROJECT_ROOT / "logs"
DATA_ROOT = PROJECT_ROOT / "data"

MANDATORY_TOOLS: dict[str, dict[str, str]] = {
    "subfinder": {"go": "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "repo": "projectdiscovery/subfinder"},
    "amass": {"go": "github.com/owasp-amass/amass/v4/...@master", "repo": "owasp-amass/amass"},
    "assetfinder": {"go": "github.com/tomnomnom/assetfinder@latest", "repo": "tomnomnom/assetfinder"},
    "nuclei": {"go": "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest", "repo": "projectdiscovery/nuclei"},
    "httpx": {"go": "github.com/projectdiscovery/httpx/cmd/httpx@latest", "repo": "projectdiscovery/httpx"},
    "waybackurls": {"go": "github.com/tomnomnom/waybackurls@latest", "repo": "tomnomnom/waybackurls"},
    "gau": {"go": "github.com/lc/gau/v2/cmd/gau@latest", "repo": "lc/gau"},
    "katana": {"go": "github.com/projectdiscovery/katana/cmd/katana@latest", "repo": "projectdiscovery/katana"},
    "naabu": {"go": "github.com/projectdiscovery/naabu/v2/cmd/naabu@latest", "repo": "projectdiscovery/naabu"},
}
