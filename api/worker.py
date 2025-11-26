"""
Background worker for content generation tasks.

This module contains the task functions that are executed by RQ workers.
Tasks include:
- Generating blog posts from investigations
- Creating social media images
- Committing results back to the public repository
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Worker")


def generate_content_task(modified_files=None):
    """
    Generate blog posts and images from investigations.

    This task:
    1. Runs the investigation manager to check for updates
    2. Generates blog posts using Gemini AI
    3. Creates social media images
    4. Commits results back to the public repository

    Args:
        modified_files: List of files modified in the triggering commit

    Returns:
        dict: Status and results of the content generation
    """
    logger.info("Starting content generation task")
    start_time = datetime.now()

    try:
        # Run the investigation manager
        result = subprocess.run(
            [sys.executable, "scripts/manage_investigations.py", "--check"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Investigation manager failed: {result.stderr}")
            return {
                "success": False,
                "error": result.stderr,
                "duration": (datetime.now() - start_time).total_seconds()
            }

        logger.info(f"Investigation manager output: {result.stdout}")

        # TODO: Add logic to commit results back to public repo
        # This would use GitPython or subprocess to:
        # 1. Clone the public repo (or pull latest)
        # 2. Copy generated blog posts to website/src/content/blog/
        # 3. Copy generated images to website/public/images/
        # 4. Commit and push changes

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Content generation completed in {duration:.2f}s")

        return {
            "success": True,
            "duration": duration,
            "stdout": result.stdout,
            "modified_files": modified_files or []
        }

    except subprocess.TimeoutExpired:
        logger.error("Content generation timed out")
        return {
            "success": False,
            "error": "Task timed out after 30 minutes",
            "duration": (datetime.now() - start_time).total_seconds()
        }
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "duration": (datetime.now() - start_time).total_seconds()
        }


def run_pipeline_task(repo_url, upload=False):
    """
    Run the full video generation pipeline for a repository.

    This is a legacy task for generating videos from repository stars.

    Args:
        repo_url: URL of the GitHub repository
        upload: Whether to upload results to cloud storage

    Returns:
        dict: Status and results of the pipeline execution
    """
    logger.info(f"Starting pipeline for {repo_url}")
    start_time = datetime.now()

    try:
        cmd = [sys.executable, "scripts/run_pipeline.py", "--repo", repo_url]
        if upload:
            cmd.append("--upload")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800  # 30 minute timeout
        )

        if result.returncode != 0:
            logger.error(f"Pipeline failed: {result.stderr}")
            return {
                "success": False,
                "repo_url": repo_url,
                "error": result.stderr,
                "duration": (datetime.now() - start_time).total_seconds()
            }

        logger.info(f"Pipeline output: {result.stdout}")

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"Pipeline completed in {duration:.2f}s")

        return {
            "success": True,
            "repo_url": repo_url,
            "duration": duration,
            "stdout": result.stdout
        }

    except subprocess.TimeoutExpired:
        logger.error(f"Pipeline timed out for {repo_url}")
        return {
            "success": False,
            "repo_url": repo_url,
            "error": "Pipeline timed out after 30 minutes",
            "duration": (datetime.now() - start_time).total_seconds()
        }
    except Exception as e:
        logger.error(f"Pipeline failed for {repo_url}: {e}")
        return {
            "success": False,
            "repo_url": repo_url,
            "error": str(e),
            "duration": (datetime.now() - start_time).total_seconds()
        }


if __name__ == "__main__":
    # For testing
    print("Worker module loaded successfully")
    print("Available tasks:")
    print("- generate_content_task")
    print("- run_pipeline_task")
