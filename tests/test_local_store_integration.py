
import sys
import os
import shutil
from pathlib import Path
import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from persistence.local_store import LocalStore

@pytest.fixture
def temp_store_dir():
    dir_path = "test_investigations_temp"
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)
    yield dir_path
    if os.path.exists(dir_path):
        shutil.rmtree(dir_path)

def test_save_and_get_investigation(temp_store_dir):
    store = LocalStore(storage_dir=temp_store_dir)
    
    repo_data = {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "html_url": "https://github.com/owner/test-repo",
        "stargazers_count": 10,
        "language": "Python",
        "latest_commit_hash": "abc123456"
    }
    
    analysis = {
        "version": "1.0.0",
        "content": "This is a test analysis."
    }
    
    # Save
    path = store.save_investigation(repo_data, analysis)
    assert os.path.exists(path)
    
    # Get
    data = store.get_investigation("owner/test-repo")
    assert data is not None
    assert data["metadata"]["repo_name"] == "test-repo"
    assert data["content"].strip() == "This is a test analysis."

def test_list_investigations(temp_store_dir):
    store = LocalStore(storage_dir=temp_store_dir)
    
    repo_data = {
        "name": "test-repo",
        "full_name": "owner/test-repo",
        "latest_commit_hash": "abc"
    }
    store.save_investigation(repo_data, {"content": "test"})
    
    items = store.list_investigations()
    assert "owner/test-repo" in items
