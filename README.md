# CyberRecon AI

CyberRecon AI is a production-grade, cross-platform, AI-powered bug bounty reconnaissance framework for authorized security testing.

## Legal and Ethical Use

This framework is strictly for:
- Authorized penetration testing
- Bug bounty reconnaissance
- Security research
- Educational lab environments

It does not include malware, persistence, credential theft, unauthorized exploitation, or destructive payloads.

## Highlights

- Cross-platform support: Windows 10/11, Kali Linux, Ubuntu, Debian
- Portable mode with local binaries in tools/windows and tools/linux
- Auto tool detection, install, verify, and update
- Async high-speed recon workflows
- Modular plugin architecture
- Rich professional CLI with detailed progress visibility
- FastAPI backend for automation and dashboards
- Optional React plus Tailwind dashboard
- **AI-powered finding prioritization and summaries**
  - Local Ollama integration (free, no internet required)
  - OpenAI ChatGPT API support (optional, for enhanced analysis)
- JSON, Markdown, and HTML reporting

## Core Recon Modules

- Subdomain enumeration
- Live host discovery
- HTTP probing
- JavaScript endpoint extraction
- Secret detection (AWS keys, JWT, GitHub tokens, etc.)
- Wayback historical URL collection
- CORS misconfiguration checks
- SSRF parameter discovery
- IDOR pattern analysis
- Screenshot and login page discovery
- Technology fingerprinting

## Project Structure

```
cyberrecon-ai/
├── core/                 # Core framework
├── modules/              # 10+ recon modules
├── plugins/              # Plugin system
├── ai/                   # AI analyzer
├── api/                  # FastAPI backend
├── dashboard/            # React frontend (optional)
├── tools/windows         # Portable Windows binaries
├── tools/linux           # Portable Linux binaries
├── output/               # Scan results and reports
├── config/               # Configuration files
├── logs/                 # Scan logs
├── cyberrecon.py         # Main CLI
├── .env                  # API keys (see API_SETUP.md)
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## Requirements

- Python 3.12+
- Optional: Go, Node.js, Docker
- Optional AI: Ollama with llama3 model, OR OpenAI API key

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Playwright browser:
   ```bash
   python -m playwright install chromium
   ```
3. Install and verify recon tools:
   ```bash
   python cyberrecon.py install
   ```
4. (Optional) Configure AI API key:
   - See [API_SETUP.md](API_SETUP.md) for ChatGPT/OpenAI or Ollama configuration

## CLI Commands

```bash
# System checks
python cyberrecon.py install       # Install missing tools
python cyberrecon.py doctor        # System health check
python cyberrecon.py update-tools  # Update all tools
python cyberrecon.py verify        # Show tool versions

# Reconnaissance
python cyberrecon.py scan target.com          # Quick scan
python cyberrecon.py scan target.com --full   # Full scan with screenshots
python cyberrecon.py recon target.com         # Alias for quick scan

# Results
python cyberrecon.py js target.com            # Show JS endpoints
python cyberrecon.py secrets target.com       # Show secrets
python cyberrecon.py cors target.com          # Show CORS issues
python cyberrecon.py screenshots target.com   # List captured screenshots
```

## Scan Progress Output

During a scan, you'll see detailed progress:

```
[+] Scan ID: 1
[+] Target: example.com
[+] Output directory: output/example.com

[*] [1/10] Running subdomain_enum...
[✓] subdomain_enum completed
  → Found 542 subdomains

[*] [2/10] Running live_hosts...
[✓] live_hosts completed
  → Found 47 live hosts

[*] [3/10] Running js_analyzer...
[✓] js_analyzer completed
  → Found 312 JS files
  → Extracted 1,847 endpoints

[*] [4/10] Running secret_detector...
[✓] secret_detector completed
  → 3 findings

[+] Prioritizing findings...
[+] Generating AI summary...
[+] Saving reports...

[✓] Scan completed!
Summary: 23 findings across 47 live hosts.
```

**Repository Ready for GitHub**

- This repository includes a `.gitignore` that excludes `.env`, `tools/`, `output/`, and other sensitive/generated files.
- Use `GITHUB_PUBLISH.md` for step-by-step instructions to push to your GitHub account.
- Use `python cyberrecon.py configure` to add your OpenAI key locally (will write to `.env`).

If you want, I can now:
- Create a release tag and draft release notes for you
- Add a GitHub Actions workflow (CI) to run lint/tests automatically (I already added one in this commit)
- Generate example screenshots and a short demo GIF for the README

- python cyberrecon.py recon target.com
- python cyberrecon.py js target.com
- python cyberrecon.py secrets target.com
- python cyberrecon.py cors target.com
- python cyberrecon.py screenshots target.com

## Authorization Gate

Before scanning, CyberRecon AI requires exact confirmation:

I confirm I have authorization to scan this target

## FastAPI Backend

Run API server:
- uvicorn api.app:app --host 0.0.0.0 --port 8000

Key endpoints:
- GET /health
- POST /scans
- GET /scans/{job_id}
- GET /findings/{scan_id}
- GET /reports/{target}
- GET /screenshots/{target}
- GET /statistics
- GET /scan-history

## Dashboard (Optional)

1. cd dashboard
2. npm install
3. npm run dev

Dashboard reads API data from http://localhost:8000.

## Docker

Build and run:
- docker compose up --build

The container exposes FastAPI on port 8000 and mounts output, reports, screenshots, and logs.

## Reporting

For each target scan, reports are generated in reports:
- target_report.json
- target_report.md
- target_report.html

Each finding includes severity, endpoint, evidence, risk score, AI summary, and remediation guidance.

## Plugin System

Create a plugin file in plugins with PLUGIN_MODULES list containing ReconModule instances.
See plugins/sample_plugin.py for template.

## Doctor Mode Checks

- Python version
- Go installation
- Node.js installation
- Playwright browser presence
- Mandatory external tool availability
- PATH and write capability checks
- Internet connectivity

## Security Notes

- Archive extraction is path-safe in GitHub release downloader.
- Portable binaries are preferred before global binaries.
- Installation failures continue gracefully with fallback methods.

## Portfolio Use

CyberRecon AI is suitable for GitHub showcases, cybersecurity internship portfolios, and practical security automation demonstrations.
