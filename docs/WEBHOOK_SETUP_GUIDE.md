# 🔗 Webhook Configuration Guide

This guide explains how to configure GitHub webhooks to enable communication between the public and private repositories.

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     PUBLIC REPO (bestof-opensorce)              │
│                                                                 │
│  1. Investigation pipeline runs (every 4 hours or manual)      │
│  2. Updates investigations/ and blog posts                     │
│  3. Commits to main branch                                     │
│  4. GitHub webhook triggers → POST to private repo             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS POST
                              │ (push event)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PRIVATE REPO (bestof-pipeline)              │
│                                                                 │
│  1. Webhook server receives POST at /webhook                   │
│  2. Verifies signature with GITHUB_WEBHOOK_SECRET              │
│  3. Enqueues content generation job                            │
│  4. Generates blog posts with Gemini AI                        │
│  5. Creates social media images                                │
│  6. Commits results back to public repo                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Step 1: Deploy Private Webhook Server

### Option A: Local Development

1. **Install dependencies:**
   ```bash
   cd bestof-pipeline
   pip install -r requirements.txt
   ```

2. **Start Redis (optional, for job queue):**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine

   # Or install Redis locally
   # Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
   # Linux: sudo apt-get install redis-server
   # macOS: brew install redis
   ```

3. **Start the webhook server:**
   ```bash
   python api/webhook_server.py
   ```

   Server will run on `http://localhost:5001`

4. **Expose to internet using ngrok:**
   ```bash
   # Install ngrok: https://ngrok.com/download
   ngrok http 5001
   ```

   Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

### Option B: Cloud Deployment (Recommended for Production)

#### Deploy to Render.com

1. Create a new **Web Service** on Render
2. Connect your private GitHub repo
3. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn api.webhook_server:app --bind 0.0.0.0:$PORT`
   - **Environment Variables:**
     ```
     GITHUB_WEBHOOK_SECRET=your-secret-here
     REDIS_URL=redis://your-redis-instance
     GOOGLE_API_KEY=your-gemini-api-key
     GITHUB_TOKEN=your-pat-token
     ```

#### Deploy to Railway.app

1. Create a new project from your private repo
2. Add Redis service
3. Configure environment variables (same as above)
4. Railway will automatically deploy

#### Deploy to Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Create `fly.toml`:
   ```toml
   app = "bestof-webhook"

   [build]
     builder = "paketobuildpacks/builder:base"

   [env]
     PORT = "8080"

   [[services]]
     http_checks = []
     internal_port = 8080
     protocol = "tcp"

     [[services.ports]]
       handlers = ["http"]
       port = 80

     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   ```
3. Deploy: `fly deploy`
4. Set secrets: `fly secrets set GITHUB_WEBHOOK_SECRET=xxx`

---

## 🔐 Step 2: Generate Webhook Secret

Generate a secure random secret for webhook verification:

```bash
# Linux/macOS
openssl rand -hex 32

# PowerShell
[System.Convert]::ToBase64String((1..32 | ForEach-Object {Get-Random -Minimum 0 -Maximum 256}))

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Save this secret!** You'll need it for both GitHub webhook configuration and your server's environment variables.

---

## 🌐 Step 3: Configure GitHub Webhook in Public Repo

1. **Go to your public repository:**
   - Navigate to: `https://github.com/iberi22/bestof-opensorce`

2. **Open Settings → Webhooks:**
   - Click "Add webhook"

3. **Configure the webhook:**
   - **Payload URL:** Your webhook server URL + `/webhook`
     - Example: `https://abc123.ngrok.io/webhook`
     - Or production: `https://bestof-webhook.fly.dev/webhook`

   - **Content type:** `application/json`

   - **Secret:** Paste the secret you generated in Step 2

   - **Which events would you like to trigger this webhook?**
     - Select "Let me select individual events"
     - Check: ✅ **Pushes**
     - Check: ✅ **Repository dispatches** (optional, for manual triggers)
     - Uncheck everything else

   - **Active:** ✅ Enabled

4. **Save webhook**

5. **Test the webhook:**
   - GitHub will send a `ping` event
   - Check the "Recent Deliveries" tab
   - Should see a ✅ with HTTP 200 response

---

## 🔑 Step 4: Configure Environment Variables

### Private Repository (bestof-pipeline)

Create or update `.env` file:

```bash
# GitHub Configuration
GITHUB_WEBHOOK_SECRET=your-secret-from-step-2
GITHUB_TOKEN=ghp_your_personal_access_token
PUBLIC_REPO_URL=https://github.com/iberi22/bestof-opensorce.git

# AI Configuration
GOOGLE_API_KEY=your-gemini-api-key

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# Server Configuration
PORT=5001
FLASK_ENV=production
```

### Required GitHub Secrets

Add these secrets to your **private repository** (Settings → Secrets and variables → Actions):

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `GITHUB_WEBHOOK_SECRET` | Same secret used in webhook config | Generated in Step 2 |
| `GOOGLE_API_KEY` | Gemini AI API key | [Google AI Studio](https://makersuite.google.com/app/apikey) |
| `GH_PAT` | Personal Access Token with repo permissions | [GitHub Settings](https://github.com/settings/tokens) |
| `REDIS_URL` | Redis connection URL (optional) | Cloud provider or `redis://localhost:6379` |

**To create a Personal Access Token (PAT):**
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "bestof-pipeline-access"
4. Select scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Actions workflows)
5. Click "Generate token"
6. Copy the token immediately (it won't be shown again!)

---

## 🧪 Step 5: Test the Integration

### Test 1: Manual Webhook Trigger

Send a test payload using curl:

```bash
# Generate signature
SECRET="your-webhook-secret"
PAYLOAD='{"ref":"refs/heads/main","commits":[{"added":["investigations/test.md"]}]}'
SIGNATURE=$(echo -n "$PAYLOAD" | openssl dgst -sha256 -hmac "$SECRET" | sed 's/^.* //')

# Send webhook
curl -X POST https://your-webhook-url.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-Hub-Signature-256: sha256=$SIGNATURE" \
  -d "$PAYLOAD"
```

Expected response:
```json
{
  "message": "Content generation triggered",
  "job_id": "abc123...",
  "status_url": "/jobs/abc123..."
}
```

### Test 2: Push to Public Repo

1. Make a change to an investigation file in the public repo
2. Commit and push to main branch
3. Check webhook server logs for activity
4. Verify the webhook delivery in GitHub (Settings → Webhooks → Recent Deliveries)

### Test 3: Check Job Status

If using Redis queue:

```bash
curl https://your-webhook-url.com/jobs/JOB_ID
```

Response:
```json
{
  "job_id": "abc123...",
  "status": "finished",
  "created_at": "2025-11-26T10:00:00",
  "ended_at": "2025-11-26T10:05:30",
  "result": {
    "success": true,
    "duration": 330.5
  }
}
```

### Test 4: Verify Content Generation

After webhook triggers:

1. Check private repo logs for content generation
2. Verify new blog posts in `output/` directory
3. Check if changes were committed back to public repo
4. Confirm blog post appears in `website/src/content/blog/`

---

## 📊 Monitoring and Debugging

### Check Webhook Health

```bash
curl https://your-webhook-url.com/health
```

Response:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "queue_available": true,
  "queue_length": 3,
  "workers_count": 2
}
```

### View Webhook Logs

**In GitHub:**
1. Go to Settings → Webhooks
2. Click on your webhook
3. Click "Recent Deliveries"
4. View request/response details

**On your server:**
```bash
# If using systemd
journalctl -u webhook-server -f

# If using Docker
docker logs -f webhook-container

# Direct Python
tail -f webhook_server.log
```

### Common Issues

#### Issue: Webhook returns 403 (Invalid signature)

**Solution:**
- Verify `GITHUB_WEBHOOK_SECRET` matches in both GitHub webhook config and server environment
- Check signature verification logic in `webhook_server.py`

#### Issue: Server not receiving webhooks

**Solution:**
- Confirm server is publicly accessible (use curl from external machine)
- Check firewall rules
- Verify ngrok tunnel is active (for local development)
- Check webhook URL is correct in GitHub settings

#### Issue: Content generation not running

**Solution:**
- Check `scripts/manage_investigations.py` exists and is executable
- Verify environment variables (`GOOGLE_API_KEY`, `GITHUB_TOKEN`) are set
- Check Redis connection if using job queue
- Review worker logs for errors

#### Issue: Changes not committed back to public repo

**Solution:**
- Verify `GH_PAT` token has correct permissions
- Check Git configuration in worker script
- Ensure public repo URL is correct
- Review commit logs for authentication errors

---

## 🔄 Workflow Summary

Once configured, the automatic workflow is:

1. **Every 4 hours** (or manual trigger):
   - Public repo runs investigation pipeline
   - Updates investigation files
   - Commits changes to main branch

2. **GitHub webhook fires:**
   - Sends POST request to private repo webhook server
   - Includes list of modified files

3. **Private repo processes:**
   - Verifies webhook signature
   - Checks if investigations were updated
   - Enqueues content generation job

4. **Content generation:**
   - Runs `manage_investigations.py --check`
   - Generates blog posts with Gemini AI
   - Creates social media images
   - Commits results back to public repo

5. **Public repo deploys:**
   - GitHub Actions detects blog post changes
   - Builds Astro site
   - Deploys to GitHub Pages

---

## 🛡️ Security Best Practices

1. **Always use HTTPS** for webhook endpoints
2. **Verify webhook signatures** on every request
3. **Use strong secrets** (32+ characters, random)
4. **Rotate secrets periodically** (every 90 days)
5. **Limit token permissions** to minimum required
6. **Monitor webhook activity** for suspicious patterns
7. **Use environment variables** for all secrets (never commit to repo)
8. **Enable rate limiting** on webhook endpoint
9. **Log security events** (failed signatures, unusual patterns)
10. **Use secret scanning** tools in your repos

---

## 📚 Additional Resources

- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)
- [Securing Webhooks](https://docs.github.com/en/webhooks/using-webhooks/securing-your-webhooks)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Redis Queue (RQ) Documentation](https://python-rq.org/)
- [TWO_REPO_ARCHITECTURE.md](../TWO_REPO_ARCHITECTURE.md) - Full architecture details

---

## 🤝 Support

For issues or questions:
- **Public repo issues:** https://github.com/iberi22/bestof-opensorce/issues
- **Private repo:** Contact repository maintainer

---

**Last Updated:** 2025-11-26
