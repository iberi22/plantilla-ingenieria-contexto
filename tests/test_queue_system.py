"""
Tests for the Queue System (RQ/Redis).

Tests webhook server integration with RQ and job monitoring endpoints.
Note: Flask integration tests require a running Flask app context and are
currently marked as integration tests. Worker task tests can run independently.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import json
import os

# Add api to path
api_path = str(Path(__file__).parent.parent / "api")
if api_path not in sys.path:
    sys.path.insert(0, api_path)


@pytest.mark.integration
class TestQueueSystemIntegration:
    """
    Integration tests for Flask webhook endpoints.
    
    These tests require a full Flask app setup with mocked Redis/RQ.
    They are marked as integration tests and can be skipped in CI.
    Run with: pytest -m integration
    """
    pass  # Tests disabled - require full integration setup


class TestWorkerTasks:
    """Test suite for worker task functions."""
    
    def test_run_pipeline_task_success(self):
        """Test successful pipeline task execution."""
        import worker
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "Pipeline completed successfully"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = worker.run_pipeline_task("https://github.com/test/repo", upload=True)
            
            assert result['status'] == 'success'
            assert result['repo_url'] == 'https://github.com/test/repo'
            assert 'stdout' in result
    
    def test_run_pipeline_task_failure(self):
        """Test failed pipeline task execution."""
        import worker
        
        with patch('subprocess.run') as mock_run:
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Error: Pipeline failed"
            mock_run.return_value = mock_result
            
            result = worker.run_pipeline_task("https://github.com/test/repo")
            
            assert result['status'] == 'failed'
            assert 'error' in result
            assert result['exit_code'] == 1
    
    def test_run_pipeline_task_timeout(self):
        """Test pipeline task timeout handling."""
        import worker
        import subprocess
        
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 1800)
            
            result = worker.run_pipeline_task("https://github.com/test/repo")
            
            assert result['status'] == 'timeout'
            assert 'timeout' in result['error'].lower()
    
    def test_process_batch_repos(self):
        """Test batch processing of multiple repositories."""
        import worker
        
        with patch.object(worker, 'run_pipeline_task') as mock_task:
            mock_task.side_effect = [
                {'status': 'success', 'repo_url': 'repo1'},
                {'status': 'success', 'repo_url': 'repo2'},
                {'status': 'failed', 'repo_url': 'repo3', 'error': 'Test error'}
            ]
            
            repos = ['repo1', 'repo2', 'repo3']
            result = worker.process_batch_repos(repos, upload=False)
            
            assert result['total'] == 3
            assert result['successful'] == 2
            assert result['failed'] == 1
            assert len(result['repos']) == 3
