import os
import sys
import hmac
import hashlib
import logging
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebhookServer")

WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "my-secret-token")

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

            # Trigger Pipeline in background
            # In production, use Celery/Redis Queue. For now, subprocess.
            try:
                # Use sys.executable to ensure we use the same environment
                subprocess.Popen([
                    sys.executable,
                    "scripts/run_pipeline.py",
                    "--repo", repo_url,
                    "--upload" # Auto upload if starred!
                ])
                return jsonify({"message": f"Pipeline triggered for {repo_url}"}), 202
            except Exception as e:
                logger.error(f"Failed to trigger pipeline: {e}")
                return jsonify({"error": "Internal Error"}), 500

    return jsonify({"message": "Event ignored"}), 200

if __name__ == '__main__':
    app.run(port=5001)
