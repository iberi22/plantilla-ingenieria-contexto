"""
RQ Worker for processing pipeline tasks.

This module defines the background tasks that can be enqueued and processed
by RQ workers. Each task runs in isolation with proper error handling and logging.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Worker")

def run_pipeline_task(repo_url: str, upload: bool = True) -> dict:
    """
    Execute the video generation pipeline for a given repository.
    
    This task is designed to be run by an RQ worker. It executes the
    run_pipeline.py script as a subprocess and captures the results.
    
    Args:
        repo_url: The GitHub repository URL to process
        upload: Whether to upload the resulting video to YouTube
        
    Returns:
        Dict with execution results including status, output, and any errors
        
    Raises:
        Exception: If the pipeline execution fails critically
    """
    logger.info(f"Starting pipeline task for {repo_url}")
    
    try:
        # Build command
        cmd = [
            sys.executable,
            "scripts/run_pipeline.py",
            "--repo", repo_url
        ]
        
        if upload:
            cmd.append("--upload")
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute pipeline with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
            cwd=Path(__file__).parent.parent
        )
        
        # Process results
        if result.returncode == 0:
            logger.info(f"Pipeline completed successfully for {repo_url}")
            return {
                "status": "success",
                "repo_url": repo_url,
                "stdout": result.stdout,
                "stderr": result.stderr if result.stderr else None
            }
        else:
            logger.error(f"Pipeline failed for {repo_url}: {result.stderr}")
            return {
                "status": "failed",
                "repo_url": repo_url,
                "error": result.stderr,
                "stdout": result.stdout,
                "exit_code": result.returncode
            }
            
    except subprocess.TimeoutExpired:
        error_msg = f"Pipeline timeout after 30 minutes for {repo_url}"
        logger.error(error_msg)
        return {
            "status": "timeout",
            "repo_url": repo_url,
            "error": error_msg
        }
        
    except Exception as e:
        error_msg = f"Unexpected error in pipeline task: {str(e)}"
        logger.exception(error_msg)
        return {
            "status": "error",
            "repo_url": repo_url,
            "error": error_msg
        }

def process_batch_repos(repo_urls: list, upload: bool = True) -> dict:
    """
    Process multiple repositories in sequence.
    
    This task can be used to batch process multiple repositories.
    Each repo is processed sequentially to avoid resource contention.
    
    Args:
        repo_urls: List of GitHub repository URLs to process
        upload: Whether to upload resulting videos
        
    Returns:
        Dict with results for all repositories
    """
    logger.info(f"Starting batch processing for {len(repo_urls)} repositories")
    
    results = {
        "total": len(repo_urls),
        "successful": 0,
        "failed": 0,
        "repos": []
    }
    
    for repo_url in repo_urls:
        try:
            result = run_pipeline_task(repo_url, upload)
            results["repos"].append(result)
            
            if result["status"] == "success":
                results["successful"] += 1
            else:
                results["failed"] += 1
                
        except Exception as e:
            logger.error(f"Failed to process {repo_url}: {e}")
            results["failed"] += 1
            results["repos"].append({
                "status": "error",
                "repo_url": repo_url,
                "error": str(e)
            })
    
    logger.info(f"Batch processing complete: {results['successful']}/{results['total']} successful")
    return results
