# GitHub Models API Integration Guide

This project uses **GitHub Models API** for AI-powered code review via your Copilot subscription.

## Why GitHub Models API?

- ✅ **No external API keys needed** - Uses GitHub token authentication
- ✅ **Free with Copilot subscription** - Leverage existing access
- ✅ **Multiple models** - gpt-4o, gpt-4o-mini, claude-3.5-sonnet, phi-4, etc.
- ✅ **REST API** - Standard HTTP calls, no deprecated CLI extensions
- ✅ **Official endpoint** - Backed by Azure AI for reliability

---

## Prerequisites

### 1. GitHub Copilot Subscription

You need an active GitHub Copilot subscription (Individual, Business, or Enterprise).

Check your status:
```powershell
gh auth status
```

Should show:
```
✓ Logged in to github.com account YOUR_USERNAME
✓ Token scopes include: 'copilot', 'repo', 'workflow', ...
```

### 2. GitHub CLI (gh)

**Windows (PowerShell):**
```powershell
winget install --id GitHub.cli
```

**Mac:**
```bash
brew install gh
```

**Linux:**
```bash
sudo apt install gh  # Debian/Ubuntu
```

### 3. Authenticate

```powershell
gh auth login
```

Follow the prompts to authenticate. The token will include `copilot` scope automatically.

---

## How It Works

### Architecture

```
┌─────────────────┐
│ discover_hidden │
│    _gems.py     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  GrokReviewer   │─────▶│ GitHub Models API│
│   (REST API)    │      │  (Azure endpoint)│
└────────┬────────┘      └──────────────────┘
         │                         │
         │ 1. Get token            │ 2. HTTP POST
         ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│ gh auth token   │      │ gpt-4o / claude  │
│ (GITHUB_TOKEN)  │      │  (AI response)   │
└─────────────────┘      └──────────────────┘
```

### Code Flow

1. **`GrokReviewer.__init__`** - Gets GitHub token from environment or `gh CLI`
2. **`review_repository()`** - Builds context from repo metadata
3. **`_call_model_with_retry()`** - HTTP POST to `https://models.inference.ai.azure.com/chat/completions`
4. **`_parse_ai_response()`** - Extracts JSON scores from response

---

## API Endpoint

**URL:**
```
https://models.inference.ai.azure.com/chat/completions
```

**Authentication:**
```
Authorization: Bearer <GITHUB_TOKEN>
```

**Request Format:**
```json
{
  "messages": [
    {"role": "system", "content": "You are a code review expert..."},
    {"role": "user", "content": "Analyze this repo..."}
  ],
  "model": "gpt-4o",
  "temperature": 0.3,
  "max_tokens": 800
}
```

**Response:**
```json
{
  "choices": [
    {
      "message": {
        "content": "{\"architecture_score\": 8, ...}"
      }
    }
  ]
}
```

---

## Available Models

| Model | Description | Speed | Quality |
|-------|-------------|-------|---------|
| **gpt-4o** | Latest GPT-4 Omni | Fast | Excellent |
| **gpt-4o-mini** | Smaller GPT-4 | Very Fast | Good |
| **claude-3.5-sonnet** | Anthropic Claude | Medium | Excellent |
| **phi-4** | Microsoft Phi-4 | Very Fast | Good |

**Change model:**
```python
reviewer = GrokReviewer(model="claude-3.5-sonnet")
```

---

## Usage

### Basic Example

```python
from src.scanner.grok_reviewer import GrokReviewer

# Initialize (auto-detects GitHub token)
reviewer = GrokReviewer(model="gpt-4o")

# Check availability
if reviewer.available:
    print("✅ GitHub Models API ready")
else:
    print("❌ GitHub token not found")

# Review repository
scores = reviewer.review_repository(repo, readme, recent_files)
print(f"Architecture: {scores['architecture']}/10")
print(f"Documentation: {scores['documentation']}/10")
```

### In discover_hidden_gems.py

```python
# No API keys needed!
pipeline = HiddenGemsPipeline(github_token=os.getenv("GITHUB_TOKEN"))

# AI reviewer automatically initialized
pipeline.discover_gems(...)
```

---

## Environment Setup

### Option 1: Use gh CLI token (Recommended)

```powershell
# Authenticate once
gh auth login

# Token automatically used
python scripts/discover_hidden_gems.py
```

### Option 2: Export GITHUB_TOKEN

```powershell
# Get token
$token = gh auth token

# Set environment variable
$env:GITHUB_TOKEN = $token

# Run script
python scripts/discover_hidden_gems.py
```

### Option 3: .env file

```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
```

---

## Error Handling

### Token Not Found

**Error:**
```
⚠️ GitHub token not available, AI reviewer disabled
💡 Make sure GITHUB_TOKEN is set or gh CLI is authenticated
```

**Fix:**
```powershell
gh auth login
```

### API Rate Limits

**Error:**
```
GitHub Models API error 429: Rate limit exceeded
```

**Fix:**
- GitHub Models API has generous limits (typically 10-15 req/min)
- Script includes automatic retry with exponential backoff
- Consider using `gpt-4o-mini` for faster, cheaper calls

### Authentication Errors

**Error:**
```
GitHub Models API error 401: Unauthorized
```

**Fix:**
```powershell
# Refresh authentication
gh auth refresh -s copilot

# Verify
gh auth status
```

---

## Troubleshooting

### Check GitHub CLI Version

```powershell
gh --version
```

Ensure version ≥ 2.40.0

### Verify Token Scopes

```powershell
gh auth status
```

Look for `Token scopes include: 'copilot'`

### Test API Directly

```powershell
$token = gh auth token

curl https://models.inference.ai.azure.com/chat/completions `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "model": "gpt-4o",
    "max_tokens": 50
  }'
```

---

## Comparison with Other Methods

| Method | Pros | Cons |
|--------|------|------|
| **GitHub Models API** ✅ | No API keys, free with Copilot, official | Requires Copilot subscription |
| xAI API | Direct access to Grok | Requires API key, rate limits |
| Gemini API | Google's AI | 15 req/min limit, requires API key |
| gh-copilot CLI | Simple CLI | ❌ **DEPRECATED** (Sept 2025) |

---

## Official Resources

- [GitHub Models Documentation](https://docs.github.com/en/github-models)
- [Azure AI Models](https://aka.ms/azureai/model-catalog)
- [GitHub CLI](https://cli.github.com/)
- [Copilot Subscription](https://github.com/features/copilot)

---

## Next Steps

1. ✅ Authenticate with `gh auth login`
2. ✅ Run `python scripts/discover_hidden_gems.py`
3. ✅ Check logs for AI review results
4. ✅ Blog posts will include AI insights

---

**Last Updated:** January 2025
**API Version:** GitHub Models v1 (Azure endpoint)
