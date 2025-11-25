# Queue System Setup Guide

## Overview

The project uses **RQ (Redis Queue)** for asynchronous task processing. This enables scalable, non-blocking execution of video generation pipelines triggered by webhooks.

## Architecture

```
GitHub Webhook → Flask API → Redis Queue → RQ Worker → Pipeline Execution
                     ↓
                Job Tracking & Status Monitoring
```

### Components

1. **Redis**: Message broker and job storage
2. **Flask API** (`api/webhook_server.py`): Receives webhooks and enqueues jobs
3. **RQ Worker** (`api/worker.py`): Processes jobs from the queue
4. **Job Tracking**: Monitor job status via REST API

## Prerequisites

### Install Redis

**Windows (via Chocolatey):**
```powershell
choco install redis-64
redis-server
```

**Windows (via Docker):**
```powershell
docker run -d -p 6379:6379 --name redis redis:alpine
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

### Verify Redis Installation
```bash
redis-cli ping
# Expected output: PONG
```

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Redis URL (optional):**
```bash
# Default: redis://localhost:6379/0
export REDIS_URL="redis://your-redis-host:6379/0"
```

## Running the System

### Option 1: Development Mode (3 terminals)

**Terminal 1 - Redis Server:**
```bash
redis-server
```

**Terminal 2 - Flask API:**
```bash
python api/webhook_server.py
```

**Terminal 3 - RQ Worker:**
```bash
rq worker pipeline_tasks --url redis://localhost:6379/0
```

### Option 2: Production Mode (Docker Compose)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: .
    command: python api/webhook_server.py
    ports:
      - "5001:5001"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
    depends_on:
      - redis

  worker:
    build: .
    command: rq worker pipeline_tasks --url redis://redis:6379/0
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    deploy:
      replicas: 2  # Run 2 workers for parallel processing

volumes:
  redis_data:
```

Run with:
```bash
docker-compose up -d
```

### Option 3: Systemd Services (Linux Production)

**Create `/etc/systemd/system/pipeline-worker.service`:**
```ini
[Unit]
Description=RQ Worker for Pipeline Tasks
After=network.target redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/op-to-video
Environment="REDIS_URL=redis://localhost:6379/0"
ExecStart=/opt/op-to-video/venv/bin/rq worker pipeline_tasks --url redis://localhost:6379/0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable pipeline-worker
sudo systemctl start pipeline-worker
sudo systemctl status pipeline-worker
```

## API Endpoints

### 1. Webhook Endpoint
**POST** `/webhook`

Receives GitHub webhooks and enqueues pipeline jobs.

**Response:**
```json
{
  "message": "Pipeline triggered for https://github.com/user/repo",
  "job_id": "abc123-def456-789",
  "status_url": "/jobs/abc123-def456-789"
}
```

### 2. Job Status
**GET** `/jobs/<job_id>`

Get detailed status of a specific job.

**Response:**
```json
{
  "job_id": "abc123-def456-789",
  "status": "started",
  "created_at": "2025-11-25T10:00:00Z",
  "started_at": "2025-11-25T10:00:05Z",
  "ended_at": null,
  "result": null,
  "error": null,
  "meta": {}
}
```

**Status values:**
- `queued`: Job waiting in queue
- `started`: Job currently processing
- `finished`: Job completed successfully
- `failed`: Job failed with error

### 3. List Jobs
**GET** `/jobs?status=all&limit=50`

List all jobs with optional filtering.

**Query Parameters:**
- `status`: Filter by status (`all`, `queued`, `started`, `finished`, `failed`)
- `limit`: Max number of jobs (default: 50, max: 100)

**Response:**
```json
{
  "count": 10,
  "jobs": [
    {
      "job_id": "abc123",
      "status": "finished",
      "ended_at": "2025-11-25T10:10:00Z"
    }
  ]
}
```

### 4. Health Check
**GET** `/health`

Check system health and queue status.

**Response:**
```json
{
  "status": "healthy",
  "redis_connected": true,
  "queue_available": true,
  "queue_length": 5,
  "workers_count": 2
}
```

## Monitoring

### View Queue Status
```bash
# List all queues
rq info --url redis://localhost:6379/0

# Monitor in real-time
rq info --url redis://localhost:6379/0 --interval 1
```

### View Job Details
```bash
# Get job by ID
curl http://localhost:5001/jobs/abc123-def456-789

# List all jobs
curl http://localhost:5001/jobs?status=all
```

### Redis CLI
```bash
# Connect to Redis
redis-cli

# List all keys
keys *

# Get queue length
llen rq:queue:pipeline_tasks

# View job data
get rq:job:abc123-def456-789
```

## Worker Management

### Scale Workers Horizontally

Run multiple workers on the same or different machines:

```bash
# Worker 1
rq worker pipeline_tasks --name worker-1 --url redis://localhost:6379/0

# Worker 2 (different terminal/machine)
rq worker pipeline_tasks --name worker-2 --url redis://localhost:6379/0

# Worker 3 with burst mode (process and exit)
rq worker pipeline_tasks --burst --url redis://localhost:6379/0
```

### Worker Options

```bash
rq worker [OPTIONS] QUEUES...

Options:
  --url TEXT              Redis URL
  --name TEXT             Worker name
  --burst                 Run in burst mode (process all jobs then exit)
  --worker-class TEXT     Worker class to use
  --job-class TEXT        Job class to use
  --queue-class TEXT      Queue class to use
  --path TEXT             Add path to Python path
  --results-ttl INTEGER   Job result TTL in seconds
  --worker-ttl INTEGER    Worker TTL in seconds
```

## Troubleshooting

### Redis Connection Error

```
Error: Could not connect to Redis at localhost:6379
```

**Solution:**
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server

# Or use Docker
docker start redis
```

### Worker Not Processing Jobs

```bash
# Check worker logs
rq worker pipeline_tasks --url redis://localhost:6379/0 --verbose

# Verify queue has jobs
rq info --url redis://localhost:6379/0
```

### Job Stuck in Queue

```bash
# Clear failed jobs
rq empty --url redis://localhost:6379/0 failed

# Requeue failed jobs
rq requeue --url redis://localhost:6379/0 --all
```

### Memory Issues

If workers are using too much memory:

```bash
# Limit worker to process one job at a time
rq worker pipeline_tasks --url redis://localhost:6379/0 --burst

# Or restart worker periodically (in systemd service)
RuntimeMaxSec=3600  # Restart after 1 hour
```

## Performance Tuning

### Optimize Job Execution

1. **Job Timeout**: Adjust in `webhook_server.py`
   ```python
   job_timeout='30m'  # Increase for longer jobs
   ```

2. **Result TTL**: How long to keep job results
   ```python
   result_ttl=86400  # 24 hours
   ```

3. **Worker Count**: More workers = more parallel jobs
   ```bash
   # Scale based on CPU cores
   NUM_WORKERS=$(($(nproc) - 1))
   ```

### Redis Configuration

Edit `redis.conf`:
```conf
# Max memory for job storage
maxmemory 2gb
maxmemory-policy allkeys-lru

# Persistence (optional)
save 900 1
save 300 10
```

## Security

### Webhook Signature Verification

Always verify GitHub webhook signatures:

```python
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
```

Set in environment:
```bash
export GITHUB_WEBHOOK_SECRET="your-secret-token"
```

### Redis Authentication

Enable Redis password:

**redis.conf:**
```conf
requirepass your-secure-password
```

**Connection URL:**
```bash
export REDIS_URL="redis://:your-secure-password@localhost:6379/0"
```

## Best Practices

1. **Always use Redis password in production**
2. **Monitor queue length** - Alert if it grows too large
3. **Set appropriate timeouts** - Prevent jobs from running forever
4. **Use burst workers** for one-off batch processing
5. **Log everything** - Enable verbose logging for debugging
6. **Scale horizontally** - Add more workers instead of increasing job timeout
7. **Clean up old jobs** - Regularly clear finished/failed jobs

## Migration from Subprocess

The system automatically falls back to subprocess mode if Redis is unavailable:

```python
if task_queue:
    # Use RQ
    job = task_queue.enqueue(...)
else:
    # Fallback to subprocess
    subprocess.Popen([...])
```

This ensures the system continues working even if Redis is down.
