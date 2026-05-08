# CyberRecon AI - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Framework (2 min)
```bash
cd cyberrecon-ai
pip install -r requirements.txt
python cyberrecon.py install
```

Expected output:
```
✓ 8/9 tools installed to tools/windows/
✓ Playwright browsers installed
```

### Step 2: Setup AI (optional, 1 min)

#### Option A: Free (Ollama)
1. Download from https://ollama.ai
2. Run: `ollama serve`
3. In another terminal: `ollama pull llama3`

#### Option B: Paid (ChatGPT)
1. Get API key: https://platform.openai.com/api-keys
2. Open `.env` file in project root
3. Find: `OPENAI_API_KEY=`
4. Add your key: `OPENAI_API_KEY=sk-proj-abc123...`
5. Save file

### Step 3: Run a Scan (2 min)
```bash
python cyberrecon.py scan example.com
```

You'll see:
- What each module is discovering
- Live subdomain count
- Live hosts found
- JS endpoints extracted
- Vulnerabilities identified
- AI summary generated

Reports saved to:
- `output/example.com/example.com_report.json` (machine-readable)
- `output/example.com/example.com_report.md` (readable)
- `output/example.com/example.com_report.html` (styled)

---

## API Key Comparison

| Feature | Ollama | OpenAI |
|---------|--------|--------|
| Cost | FREE | $0.05-0.25/scan |
| Setup | Download app | Get API key |
| Internet | No | Yes |
| Speed | ~10-30s per scan | ~2-5s per scan |
| Accuracy | Good | Better |
| Privacy | All local | Data sent to OpenAI |
| Availability | Offline | Requires API quota |

---

## Usage Examples

### Quick Scan (no screenshots)
```bash
python cyberrecon.py scan target.com
```

### Full Scan (with screenshots)
```bash
python cyberrecon.py scan target.com --full
```

### View Results
```bash
# Show all findings
cat output/target.com/target.com_report.md

# Show only secrets
python cyberrecon.py secrets target.com

# Show only CORS issues
python cyberrecon.py cors target.com

# List screenshots
python cyberrecon.py screenshots target.com
```

---

## Troubleshooting

### Tools won't install?
```bash
# Install manually
python cyberrecon.py doctor    # See what's missing
python cyberrecon.py install   # Try again
```

### AI summary not working?

**If using Ollama:**
```bash
# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Pull model if missing
ollama pull llama3
```

**If using OpenAI:**
```bash
# Check if .env file exists in project root
ls -la .env

# Verify API key format (must start with sk-)
cat .env | grep OPENAI_API_KEY

# Check account balance: https://platform.openai.com/account/billing/overview
```

### Scan running slowly?
- Increase concurrency in `config/default.yaml`: `concurrency: 160`
- Use `--full` flag only when needed (screenshots are slow)

---

## Next Steps

- Check [API_SETUP.md](API_SETUP.md) for detailed API configuration
- See [modules/](modules/) for what each recon module does
- Review [reports/](reports/) for output formats
- Build custom plugins in [plugins/](plugins/)

---

## Command Reference

| Command | Purpose |
|---------|---------|
| `install` | Install/verify all recon tools |
| `doctor` | System health check |
| `verify` | Show tool versions |
| `update-tools` | Refresh all tools to latest |
| `scan target.com` | Quick reconnaissance |
| `scan target.com --full` | Full scan + screenshots |
| `recon target.com` | Alias for quick scan |
| `js target.com` | Show JS endpoints |
| `secrets target.com` | Show leaked secrets |
| `cors target.com` | Show CORS vulnerabilities |
| `screenshots target.com` | List captured screenshots |

---

## Legal Reminder

Always ensure you have **written authorization** before scanning any target.

Running unauthorized security scans is illegal. This tool is for:
- ✓ Authorized penetration testing
- ✓ Bug bounty reconnaissance
- ✓ Security research with permission
- ✓ Educational labs

Not for:
- ✗ Unauthorized scanning
- ✗ Malicious purposes
- ✗ Competition sabotage
