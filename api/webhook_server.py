import os
import sys
import hmac
import hashlib
import logging
from flask import Flask, request, jsonify
from redis import Redis
from rq import Queue
from rq.job import Job

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebhookServer")

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "my-secret-token")

# Initialize Redis connection and RQ Queue
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
try:
    redis_conn = Redis.from_url(redis_url)
    redis_conn.ping()  # Test connection
    task_queue = Queue('pipeline_tasks', connection=redis_conn)
    logger.info(f"Connected to Redis at {redis_url}")
except Exception as e:
    logger.error(f"Failed to connect to Redis: {e}")
    logger.warning("Running in fallback mode without queue support")
    redis_conn = None
    task_queue = None

def verify_signature(payload, signature):
    """
    Verify that the payload was sent from GitHub by validating SHA256.

    Args:
        payload: Raw body of the request.
        signature: The 'X-Hub-Signature-256' header.
    """
    if not signature:
        return False

    sha_name, signature = signature.split('=')
    if sha_name != 'sha256':
        return False

    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """
    Handle GitHub webhooks.
    Triggers pipeline on 'star' events (created).
    """
    signature = request.headers.get('X-Hub-Signature-256')

    # Verify signature
    if not verify_signature(request.data, signature):
        logger.warning("Invalid signature attempt.")
        return jsonify({"error": "Invalid signature"}), 403

    event = request.headers.get('X-GitHub-Event', 'ping')

    if event == 'ping':
        return jsonify({"message": "Pong!"}), 200

    if event == 'star':
        data = request.json
        action = data.get('action')

        if action == 'created':
            repo_url = data['repository']['html_url']
            logger.info(f"New Star detected on {repo_url}! Triggering pipeline...")

            # Trigger Pipeline using RQ Queue
            try:
                if task_queue:
                    # Enqueue the job
                    job = task_queue.enqueue(
                        'api.worker.run_pipeline_task',
                        repo_url,
                        upload=True,
                        job_timeout='30m',  # 30 minute timeout
                        result_ttl=86400    # Keep results for 24 hours
                    )
                    logger.info(f"Job {job.id} enqueued for {repo_url}")
                    return jsonify({
                        "message": f"Pipeline triggered for {repo_url}",
                        "job_id": job.id,
                        "status_url": f"/jobs/{job.id}"
                    }), 202
                else:
                    # Fallback to subprocess if Redis is unavailable
                    import subprocess
                    subprocess.Popen([
                        sys.executable,
                        "scripts/run_pipeline.py",
                        "--repo", repo_url,
                        "--upload"
                    ])
                    logger.warning("Using subprocess fallback (Redis unavailable)")
                    return jsonify({
                        "message": f"Pipeline triggered for {repo_url} (fallback mode)",
                        "warning": "No job tracking available"
                    }), 202
            except Exception as e:
                logger.error(f"Failed to trigger pipeline: {e}")
                return jsonify({"error": "Internal Error", "details": str(e)}), 500

    return jsonify({"message": "Event ignored"}), 200

@app.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Get the status and details of a queued job.
    
    Returns job status, progress, and results if available.
    """
    if not redis_conn:
        return jsonify({"error": "Queue system unavailable"}), 503
    
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        
        response = {
            "job_id": job.id,
            "status": job.get_status(),
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "ended_at": job.ended_at.isoformat() if job.ended_at else None,
            "result": job.result if job.is_finished else None,
            "error": str(job.exc_info) if job.is_failed else None,
            "meta": job.meta
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Failed to fetch job {job_id}: {e}")
        return jsonify({"error": "Job not found", "details": str(e)}), 404

@app.route('/jobs', methods=['GET'])
def list_jobs():
    """
    List all jobs in the queue.
    
    Query params:
        - status: Filter by status (queued, started, finished, failed)
        - limit: Maximum number of jobs to return (default: 50)
    """
    if not task_queue or not redis_conn:
        return jsonify({"error": "Queue system unavailable"}), 503
    
    try:
        status_filter = request.args.get('status', 'all')
        limit = min(int(request.args.get('limit', 50)), 100)
        
        jobs_list = []
        
        # Get jobs by status
        if status_filter in ['all', 'queued']:
            queued_jobs = task_queue.jobs[:limit]
            jobs_list.extend([{
                "job_id": job.id,
                "status": "queued",
                "created_at": job.created_at.isoformat() if job.created_at else None
            } for job in queued_jobs])
        
        if status_filter in ['all', 'started']:
            started_registry = task_queue.started_job_registry
            for job_id in list(started_registry.get_job_ids())[:limit]:
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    jobs_list.append({
                        "job_id": job.id,
                        "status": "started",
                        "started_at": job.started_at.isoformat() if job.started_at else None
                    })
                except:
                    pass
        
        if status_filter in ['all', 'finished']:
            finished_registry = task_queue.finished_job_registry
            for job_id in list(finished_registry.get_job_ids())[:limit]:
                try:
                    job = Job.fetch(job_id, connection=redis_conn)
                    jobs_list.append({
                        "job_id": job.id,
                        "status": "finished",
                        "ended_at": job.ended_at.isoformat() if job.ended_at else None
                    })
                except:
                    pass
        
        return jsonify({
            "count": len(jobs_list),
            "jobs": jobs_list[:limit]
        }), 200
        
    except Exception as e:
        logger.error(f"Failed to list jobs: {e}")
        return jsonify({"error": "Failed to list jobs", "details": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    health = {
        "status": "healthy",
        "redis_connected": redis_conn is not None,
        "queue_available": task_queue is not None
    }
    
    if task_queue:
        try:
            health["queue_length"] = len(task_queue)
            health["workers_count"] = len(task_queue.workers)
        except:
            pass
    
    status_code = 200 if health["redis_connected"] else 503
    return jsonify(health), status_code

if __name__ == '__main__':
    app.run(port=5001)
