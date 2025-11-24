# Deployment Guide

## 1. Infrastructure Overview

The Video Generator ecosystem consists of:
1.  **Flask API:** Handles voice processing, translation, and video generation.
2.  **Webhook Server:** Listens for GitHub events to trigger automation.
3.  **React Frontend:** User interface for manual voice studio.
4.  **Jekyll Blog:** Static site hosting the generated content.

## 2. Docker Deployment (Recommended)

### Backend (API + Webhook)

Create a `Dockerfile` in the root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# Copy code
COPY . .

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Expose ports
EXPOSE 5000 5001

# Start script
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:5000 api.multilingual_api:app & python3 api/webhook_server.py"]
```

Run with:
```bash
docker build -t video-generator .
docker run -p 5000:5000 -p 5001:5001 --env-file .env video-generator
```

## 3. Manual Deployment

### Prerequisites
- Python 3.11+
- Node.js 18+
- FFmpeg
- Redis (optional, for async queues if implemented)

### Steps

1.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    playwright install
    ```

2.  **Start API:**
    ```bash
    python api/multilingual_api.py
    ```

3.  **Start Webhook Server:**
    ```bash
    python api/webhook_server.py
    ```

4.  **Build Frontend:**
    ```bash
    cd web
    npm install
    npm run build
    # Serve 'dist' folder with Nginx or serve
    ```

5.  **Build Blog:**
    ```bash
    cd blog
    bundle install
    bundle exec jekyll build
    # Serve '_site' folder
    ```

## 4. Environment Variables

Ensure `.env` is configured in the production environment:

```bash
OPENAI_API_KEY=...
GITHUB_TOKEN=...
FIREBASE_CREDENTIALS=...
YOUTUBE_CLIENT_SECRET_FILE=...
YOUTUBE_TOKEN_FILE=...
GITHUB_WEBHOOK_SECRET=...
```
