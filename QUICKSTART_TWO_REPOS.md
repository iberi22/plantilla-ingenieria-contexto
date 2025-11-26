# 🚀 Quick Start Guide - Two-Repo Architecture

This guide helps you quickly work with the split repository architecture.

---

## 📍 Quick Links

| Repository | Type | URL |
|------------|------|-----|
| **bestof-opensorce** | PUBLIC | https://github.com/iberi22/bestof-opensorce |
| **bestof-pipeline** | PRIVATE | https://github.com/iberi22/bestof-pipeline |
| **Live Website** | - | https://iberi22.github.io/bestof-opensorce |

---

## 🎯 Common Tasks

### 1️⃣ Add a New Investigation (Manual)

**In PUBLIC repo:**

```bash
# Create new markdown file in investigations/
cd investigations/
echo "---
url: https://github.com/owner/repo
name: Project Name
category: web-framework
language: JavaScript
stars: 10000
status: active
reviewed: false
---

Brief description of the project.
" > new-investigation.md

# Commit and push
git add investigations/new-investigation.md
git commit -m "feat: Add investigation for Project Name"
git push origin main
```

**Trigger content generation:**

```bash
# This triggers the private repo to generate blog post
curl -X POST \
  -H "Authorization: Bearer $PRIVATE_REPO_PAT" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/iberi22/bestof-pipeline/dispatches \
  -d '{"event_type":"generate-content"}'
```

---

### 2️⃣ Run Scanner to Discover New Repos

**In PUBLIC repo:**

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run scanner
python scripts/run_scanner.py

# Scanner will:
# - Search GitHub for trending repos
# - Create markdown files in investigations/
# - Commit and push automatically
```

**Scanner runs automatically every 4 hours via GitHub Actions.**

---

### 3️⃣ Generate Blog Post from Investigation

**In PRIVATE repo:**

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Configure .env file
cp .env.example .env
# Edit .env with your API keys

# Run blog generator
python scripts/manage_investigations.py --check

# This will:
# 1. Pull latest investigations from public repo
# 2. Generate blog posts with Gemini AI
# 3. Create social media images
# 4. Commit back to public repo
```

---

### 4️⃣ Deploy Blog Website (Astro)

**In PUBLIC repo:**

```bash
cd website/
npm install
npm run build

# Preview locally
npm run preview

# Deploy to GitHub Pages (automatic on push to main)
git push origin main
```

**GitHub Actions automatically builds and deploys on every push.**

---

### 5️⃣ Test Video Generation (Future)

**In PRIVATE repo:**

```bash
# Generate video from specific investigation
python scripts/generate_reel_from_post.py https://github.com/owner/repo

# This will:
# 1. Generate TTS narration
# 2. Create video with subtitles
# 3. Upload to S3/YouTube
# 4. Update investigation metadata
```

**⚠️ Note:** Video generation is currently not implemented. Coming in Phase 2.

---

## 🔧 Development Workflows

### Frontend Development (Astro Blog)

```bash
# PUBLIC repo
cd website/
npm run dev  # Opens http://localhost:4321

# Make changes to:
# - src/pages/*.astro (page layouts)
# - src/content/blog/*.md (blog posts)
# - src/components/*.svelte (UI components)

# Hot reload is enabled - changes appear instantly
```

### Frontend Development (React Dashboard)

```bash
# PUBLIC repo
cd web/
npm run dev  # Opens http://localhost:5173

# Features:
# - Voice recorder
# - Transcription display
# - Translation UI
```

### Backend Development (Flask API)

```bash
# PRIVATE repo
cd api/
python multilingual_api.py  # Starts Flask server on :5000

# Endpoints:
# POST /webhook - Receives GitHub webhooks
# POST /generate - Triggers content generation
# GET /status - Check job status
```

---

## 📝 Commit Message Convention

Use conventional commits for consistency:

```bash
# Feature
git commit -m "feat: Add new investigation for React"

# Bug fix
git commit -m "fix: Correct typo in blog post"

# Documentation
git commit -m "docs: Update setup instructions"

# Refactor
git commit -m "refactor: Simplify scanner logic"

# Chore (dependencies, config)
git commit -m "chore: Update dependencies"

# CI/CD
git commit -m "ci: Fix GitHub Actions workflow"
```

---

## 🐛 Troubleshooting

### Issue: Scanner not finding repos

```bash
# Check GitHub token
echo $GITHUB_TOKEN

# Verify token permissions:
# - repo (read)
# - public_repo (read)

# Test scanner manually
python scripts/run_scanner.py --debug
```

### Issue: Blog generation fails

```bash
# Check Gemini API key
echo $GOOGLE_API_KEY

# Test API connection
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"

# Run with verbose logging
python scripts/manage_investigations.py --check --verbose
```

### Issue: Website not building

```bash
# Clear cache
cd website/
rm -rf dist/ .astro/

# Reinstall dependencies
rm -rf node_modules/ package-lock.json
npm install

# Build again
npm run build
```

### Issue: Webhook not triggering

```bash
# Check webhook secret matches in both repos
# PUBLIC: Settings → Secrets → PUBLIC_WEBHOOK_SECRET
# PRIVATE: Settings → Secrets → PRIVATE_REPO_PAT

# Test webhook manually
curl -X POST \
  -H "Authorization: Bearer $PRIVATE_REPO_PAT" \
  https://api.github.com/repos/iberi22/bestof-pipeline/dispatches \
  -d '{"event_type":"generate-content","client_payload":{"test":true}}'
```

---

## 📊 Monitoring

### Check GitHub Actions Status

**PUBLIC repo:**
```bash
# View recent workflow runs
gh run list --repo iberi22/bestof-opensorce --limit 5

# View logs for specific run
gh run view <run-id> --log
```

**PRIVATE repo:**
```bash
gh run list --repo iberi22/bestof-pipeline --limit 5
```

### Check Website Deployment

```bash
# View deployment status
gh deployment list --repo iberi22/bestof-opensorce

# Open live site
open https://iberi22.github.io/bestof-opensorce
```

---

## 🔄 Syncing Local Repos

### Update PUBLIC repo

```bash
cd E:\scripts-python\op-to-video
git pull origin main
pip install -r requirements.txt  # If dependencies changed
cd website && npm install  # If package.json changed
```

### Update PRIVATE repo

```bash
cd E:\scripts-python\bestof-pipeline
git pull origin main
pip install -r requirements.txt  # If dependencies changed
```

---

## 🚨 Emergency Rollback

If something goes wrong:

### Rollback PUBLIC repo

```bash
# View commit history
git log --oneline -10

# Reset to previous commit
git reset --hard <commit-hash>

# Force push (⚠️ DANGER)
git push origin main --force
```

### Rollback PRIVATE repo

```bash
# Same process
cd E:\scripts-python\bestof-pipeline
git reset --hard <commit-hash>
git push origin main --force
```

---

## 📚 Additional Resources

- **Astro Docs:** https://docs.astro.build
- **Gemini AI API:** https://ai.google.dev/docs
- **GitHub Actions:** https://docs.github.com/actions
- **Markdown Guide:** https://www.markdownguide.org

---

**Last Updated:** 2025-01-23  
**Version:** 1.0  
**Status:** ✅ Production Ready
