# CyberRecon AI Windows Setup

## Supported
- Windows 10
- Windows 11

## Prerequisites
- Python 3.12+
- PowerShell
- Optional: Scoop, Chocolatey, Go, Node.js

## Steps

1. Open PowerShell in project root.
2. Install Python dependencies:
   - pip install -r requirements.txt
3. Install Playwright browser:
   - python -m playwright install chromium
4. Run tool installation:
   - python cyberrecon.py install
5. Validate environment:
   - python cyberrecon.py doctor

## Installer Priority

Windows installer fallback order used by ToolManager:
1. Scoop
2. Chocolatey
3. Go install
4. GitHub release binaries

## Portable Binary Location

- tools/windows

If a tool exists there, CyberRecon AI uses it before global PATH.

## Running a Full Scan

- python cyberrecon.py scan example.com --full

## Troubleshooting

- If Playwright browsers are missing, rerun:
  - python -m playwright install chromium
- If Scoop is missing:
  - iwr -useb get.scoop.sh | iex
- If a tool fails to install, run doctor and inspect logs/cyberrecon.log.
