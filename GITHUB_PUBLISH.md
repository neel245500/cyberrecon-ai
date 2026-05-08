# Publishing `cyberrecon-ai` to GitHub (public)

This guide helps you prepare and publish the project to GitHub safely and professionally.

1) Prepare repository locally

```bash
cd path/to/cyberrecon-ai
git init
git add .gitignore
git add README.md QUICKSTART.md API_SETUP.md GITHUB_PUBLISH.md
git add core modules ai api dashboard pyproject.toml requirements.txt
git commit -m "chore: initial project import - cyberrecon-ai"
```

Notes:
- Do NOT add `.env` or `tools/` binaries to the repo (they are in `.gitignore`).
- Keep large binary bundles out of repo; users use `python cyberrecon.py install` to fetch tools.

2) Create repository on GitHub

- Go to https://github.com/new
- Repository name: `cyberrecon-ai`
- Description (short): "AI-powered bug bounty reconnaissance framework — authorized testing only."
- Public repository: yes
- Initialize without README (you already have one locally)

3) Add remote & push

```bash
git remote add origin https://github.com/<your-username>/cyberrecon-ai.git
git branch -M main
git push -u origin main
```

4) Recommended repository files

- `README.md` — High-level project summary, usage, quickstart.
- `API_SETUP.md` — How to configure OpenAI / Ollama keys.
- `QUICKSTART.md` — 5-minute setup and example commands.
- `GITHUB_PUBLISH.md` — (this file) publishing checklist and description templates.
- `LICENSE` — Choose a license (MIT recommended for recon tools).

5) Suggested README short description (for the repo page)

Title: CyberRecon AI — AI-powered Recon Framework

One-line: "A modular, cross-platform reconnaissance framework with AI-powered prioritization and summaries (for authorized testing)."

Longer description (use in repo README / GitHub description):

"CyberRecon AI is a production-grade, cross-platform reconnaissance framework designed for authorized penetration testing and bug bounty reconnaissance. It integrates modular recon modules (subdomain enumeration, live host discovery, JavaScript analysis, secret detection, CORS/SSRF/IDOR checks, screenshots) with optional AI-powered prioritization and concise summaries via local Ollama or OpenAI's ChatGPT. Tools are installed on-demand using `python cyberrecon.py install` — large binaries are intentionally not stored in the repository."

6) Suggested `README.md` sections to include (order):
- Title + short description
- Legal & Ethical Use (prominent)
- Quickstart (link to `QUICKSTART.md`)
- Installation (dependencies and `install` command)
- Usage examples (scan, recon, full scan)
- Configuration (link `API_SETUP.md` for keys)
- Contribution guide (how to add modules/plugins)
- License

7) Screenshots / Design assets

- Capture these screenshots (use 1280×720 or 1920×1080):
  - CLI running a sample scan showing per-module progress and final summary
  - Generated HTML report (styled) opened in browser
  - Dashboard screenshot (if you plan to enable the React UI)

- Add a `/screenshots` folder with 3-5 PNG images. In the README use:

  ![CLI scan running](screenshots/cli_scan.png)
  ![HTML report](screenshots/report.png)

8) Releases and tags

- Tag a release when ready:
  ```bash
  git tag -a v0.1.0 -m "Initial public release"
  git push origin v0.1.0
  ```
- Add release notes: highlight legal usage, quick install, and sample results.

9) Security & responsible disclosure

- Add SECURITY.md describing how to responsibly disclose vulnerabilities found in the project.
- Add a `CODE_OF_CONDUCT.md` if you expect contributions.

10) Socials & visibility

- Add topics/tags: `recon`, `bug-bounty`, `security`, `python`, `fastapi`, `playwright`.
- Add a short demo GIF (optional) in `screenshots/` and link in README.

Commit message examples:

- "feat: add CLI configure command and publish docs"
- "docs: add GitHub publishing guide and quickstart"

Finally: push your final README and docs, create a release, and publish. Congratulations!
