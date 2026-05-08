# CyberRecon AI - API Key Setup Guide

## ChatGPT / OpenAI API

### Why use OpenAI?
- More accurate vulnerability analysis
- Better remediation suggestions
- Faster than local Ollama
- Requires paid OpenAI account

### How to get API key:

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Click "API keys" in left sidebar
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Where to put API key:

**Option 1: Using .env file (Recommended)**
1. Open `.env` file in project root
2. Find line: `OPENAI_API_KEY=`
3. Paste your key: `OPENAI_API_KEY=sk-YOUR_KEY_HERE`
4. Save file
5. Restart scan command

Example:
```
OPENAI_API_KEY=sk-proj-abc123xyz...
OPENAI_MODEL=gpt-4
```

**Option 2: Using environment variable**
```bash
$env:OPENAI_API_KEY = "sk-your-key-here"
python cyberrecon.py scan example.com
```

**Option 3: Using config/default.yaml**
```yaml
settings:
  openai_enabled: true
  openai_api_key: sk-your-key-here
```

### Cost estimate:
- Small scan (100 findings): ~$0.05
- Large scan (500 findings): ~$0.25
- Monitor usage at: https://platform.openai.com/account/billing/overview

---

## Ollama (Local AI - FREE)

### Why use Ollama?
- Free
- No internet needed
- Privacy-focused
- Slower but functional

### Setup:

1. Download from [ollama.ai](https://ollama.ai)
2. Install and run: `ollama serve`
3. In another terminal: `ollama pull llama3`
4. Default settings in `.env` are already configured

### Config in .env:
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

## What happens during scan:

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

[+] Prioritizing findings...
[+] Generating AI summary...
[+] Saving reports...

[✓] Scan completed!
Summary: 23 findings across 47 live hosts.
```

---

## Using without API keys

CyberRecon works fine without any API keys:
- Offline analysis (CORS, SSRF, IDOR, etc.) ✓
- Security headers checks ✓
- Secret pattern detection ✓
- Screenshots and tech fingerprinting ✓
- Local Ollama summaries (if running)

Only **AI summaries require** API or Ollama.

---

## Troubleshooting

### OpenAI returns error:
- Check API key format (must start with `sk-`)
- Verify key is not revoked at https://platform.openai.com/api-keys
- Check account balance/credits

### Ollama not responding:
- Start ollama: `ollama serve`
- Verify port 11434 is open: `netstat -an | findstr 11434`
- Pull model if missing: `ollama pull llama3`

### .env not loading:
- Restart terminal/IDE
- Verify .env is in project root (same folder as cyberrecon.py)
- Check syntax: no spaces around `=`
