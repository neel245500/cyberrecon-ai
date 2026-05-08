# CyberRecon AI Linux Setup

## Supported
- Kali Linux
- Ubuntu
- Debian

## Prerequisites
- Python 3.12+
- apt
- Optional: Go, Node.js

## Steps

1. Open terminal in project root.
2. Install dependencies:
   - pip install -r requirements.txt
3. Install Playwright browser:
   - python -m playwright install chromium
4. Install tools:
   - python cyberrecon.py install
5. Verify environment:
   - python cyberrecon.py doctor

## Installer Strategy

Linux installer fallback order used by ToolManager:
1. apt install
2. go install
3. GitHub release binaries

## Portable Binary Location

- tools/linux

If binaries exist there, they are used directly.

## Running a Full Scan

- python cyberrecon.py scan example.com --full

## Troubleshooting

- If apt package is unavailable, installer automatically tries Go and GitHub release fallback.
- For permission issues, ensure write access for output, reports, and tools directories.
- Inspect logs/cyberrecon.log for detailed install and scan traces.
