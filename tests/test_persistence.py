"""
Unit tests for Firebase persistence module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.persistence.firebase_store import FirebaseStore


@pytest.fixture
def mock_firebase():
    """Mock Firebase Admin SDK."""
    with patch('src.persistence.firebase_store.firebase_admin') as mock_admin, \
         patch('src.persistence.firebase_store.firestore') as mock_firestore:

        # Mock the app check
        mock_admin._apps = {}

        # Mock Firestore client
        mock_db = MagicMock()
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_firestore.client.return_value = mock_db

        yield {
            'admin': mock_admin,
            'firestore': mock_firestore,
            'db': mock_db,
            'collection': mock_collection
        }


@pytest.fixture
def firebase_store(mock_firebase, tmp_path):
    """Create FirebaseStore instance with mocked credentials."""
    # Create a temporary credentials file
    creds_file = tmp_path / "creds.json"
    creds_file.write_text('{"type": "service_account", "project_id": "test"}')

    with patch('src.persistence.firebase_store.credentials.Certificate'):
        store = FirebaseStore(credentials_path=str(creds_file))
        return store


class TestFirebaseStore:
    """Test suite for FirebaseStore class."""

    def test_initialization_with_file_path(self, tmp_path, mock_firebase):
        """Test initialization with credentials file path."""
        creds_file = tmp_path / "creds.json"
        creds_file.write_text('{"type": "service_account"}')

        with patch('src.persistence.firebase_store.credentials.Certificate'):
            store = FirebaseStore(credentials_path=str(creds_file))
            assert store.db is not None
            assert store.collection is not None

    def test_initialization_with_env_var(self, tmp_path, mock_firebase, monkeypatch):
        """Test initialization with environment variable."""
        creds_file = tmp_path / "creds.json"
        creds_file.write_text('{"type": "service_account"}')

        monkeypatch.setenv("FIREBASE_CREDENTIALS", str(creds_file))

        with patch('src.persistence.firebase_store.credentials.Certificate'):
            store = FirebaseStore()
            assert store.db is not None

    def test_initialization_without_credentials(self, mock_firebase):
        """Test that initialization fails without credentials."""
        with pytest.raises(ValueError, match="(Firebase credentials required|FIREBASE_CREDENTIALS must be)"):
            FirebaseStore()

    def test_is_processed_returns_true_for_existing_repo(self, firebase_store, mock_firebase):
        """Test is_processed returns True for existing repository."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_firebase['collection'].document.return_value.get.return_value = mock_doc

        result = firebase_store.is_processed("owner/repo")

        assert result is True
        mock_firebase['collection'].document.assert_called_with("owner/repo")

    def test_is_processed_returns_false_for_new_repo(self, firebase_store, mock_firebase):
        """Test is_processed returns False for new repository."""
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_firebase['collection'].document.return_value.get.return_value = mock_doc

        result = firebase_store.is_processed("owner/new-repo")

        assert result is False

    def test_is_processed_handles_errors_gracefully(self, firebase_store, mock_firebase):
        """Test is_processed returns False on error (fail-safe)."""
        mock_firebase['collection'].document.return_value.get.side_effect = Exception("Network error")

        result = firebase_store.is_processed("owner/repo")

        assert result is False  # Fail-safe behavior

    def test_save_repo_success(self, firebase_store, mock_firebase):
        """Test successful repository save."""
        repo_data = {
            "description": "Test repo",
            "stargazers_count": 100,
            "language": "Python",
            "html_url": "https://github.com/owner/repo"
        }

        result = firebase_store.save_repo("owner/repo", repo_data, status="pending")

        assert result is True
        mock_firebase['collection'].document.return_value.set.assert_called_once()

        # Verify the data structure
        call_args = mock_firebase['collection'].document.return_value.set.call_args[0][0]
        assert call_args["repo_name"] == "owner/repo"
        assert call_args["description"] == "Test repo"
        assert call_args["stars"] == 100
        assert call_args["status"] == "pending"

    def test_save_repo_handles_missing_fields(self, firebase_store, mock_firebase):
        """Test save_repo handles missing optional fields."""
        repo_data = {}  # Empty data

        result = firebase_store.save_repo("owner/repo", repo_data)

        assert result is True
        call_args = mock_firebase['collection'].document.return_value.set.call_args[0][0]
        assert call_args["description"] == ""
        assert call_args["stars"] == 0
        assert call_args["language"] == "Unknown"

    def test_save_repo_handles_errors(self, firebase_store, mock_firebase):
        """Test save_repo returns False on error."""
        mock_firebase['collection'].document.return_value.set.side_effect = Exception("Write error")

        result = firebase_store.save_repo("owner/repo", {})

        assert result is False

    def test_update_status_with_video_url(self, firebase_store, mock_firebase):
        """Test updating status with video URL."""
        result = firebase_store.update_status(
            "owner/repo",
            status="completed",
            video_url="https://youtube.com/watch?v=123"
        )

        assert result is True
        call_args = mock_firebase['collection'].document.return_value.update.call_args[0][0]
        assert call_args["status"] == "completed"
        assert call_args["video_url"] == "https://youtube.com/watch?v=123"

    def test_update_status_with_error(self, firebase_store, mock_firebase):
        """Test updating status with error message."""
        result = firebase_store.update_status(
            "owner/repo",
            status="failed",
            error_message="Upload failed"
        )

        assert result is True
        call_args = mock_firebase['collection'].document.return_value.update.call_args[0][0]
        assert call_args["status"] == "failed"
        assert call_args["error_message"] == "Upload failed"

    def test_get_repo_existing(self, firebase_store, mock_firebase):
        """Test retrieving existing repository."""
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"repo_name": "owner/repo", "status": "completed"}
        mock_firebase['collection'].document.return_value.get.return_value = mock_doc

        result = firebase_store.get_repo("owner/repo")

        assert result is not None
        assert result["repo_name"] == "owner/repo"
        assert result["status"] == "completed"

    def test_get_repo_not_found(self, firebase_store, mock_firebase):
        """Test retrieving non-existent repository."""
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_firebase['collection'].document.return_value.get.return_value = mock_doc

        result = firebase_store.get_repo("owner/nonexistent")

        assert result is None

    def test_get_recent_repos(self, firebase_store, mock_firebase):
        """Test retrieving recent repositories."""
        mock_docs = [
            MagicMock(to_dict=lambda: {"repo_name": "owner/repo1"}),
            MagicMock(to_dict=lambda: {"repo_name": "owner/repo2"}),
        ]

        mock_query = MagicMock()
        mock_query.stream.return_value = mock_docs
        mock_firebase['collection'].order_by.return_value.limit.return_value = mock_query

        result = firebase_store.get_recent_repos(limit=2)

        assert len(result) == 2
        assert result[0]["repo_name"] == "owner/repo1"
        assert result[1]["repo_name"] == "owner/repo2"
