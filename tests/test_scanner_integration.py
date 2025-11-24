import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.github_scanner import GitHubScanner

class TestGitHubScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = GitHubScanner(token="dummy_token")

    @patch('requests.get')
    def test_scan_recent_repos(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"id": 1, "name": "repo1"}]}
        mock_get.return_value = mock_response

        repos = self.scanner.scan_recent_repos(limit=5)
        self.assertEqual(len(repos), 1)
        self.assertEqual(repos[0]["name"], "repo1")

    @patch('requests.get')
    def test_validate_repo_valid(self, mock_get):
        # Mock validation calls (Readme, CI)
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Return different values based on URL
        def side_effect(url, headers):
            if "/readme" in url:
                return MagicMock(status_code=200, json=lambda: {"size": 1000})
            if "/actions/runs" in url:
                return MagicMock(status_code=200, json=lambda: {"workflow_runs": [{}]})
            return MagicMock(status_code=404)

        mock_get.side_effect = side_effect

        repo = {
            "full_name": "owner/valid-repo",
            "name": "valid-repo",
            "description": "This is a very good description for a valid repo.",
            "license": {"key": "mit"},
            "archived": False,
            "disabled": False
        }

        is_valid = self.scanner.validate_repo(repo)
        self.assertTrue(is_valid)

    @patch('requests.get')
    def test_validate_repo_invalid(self, mock_get):
        # Mock validation calls (Readme too small)
        mock_response = MagicMock()
        mock_response.status_code = 200
        def side_effect(url, headers):
            if "/readme" in url:
                return MagicMock(status_code=200, json=lambda: {"size": 100}) # Too small
            return MagicMock(status_code=200)

        mock_get.side_effect = side_effect

        repo = {
            "full_name": "owner/small-repo",
            "name": "small-repo",
            "description": "Short desc.", # Too short if logic checks length, but here it might pass description check if logic changed, let's rely on readme
            "license": {"key": "mit"},
            "archived": False
        }

        # Logic check: description < 20
        is_valid = self.scanner.validate_repo(repo)
        self.assertFalse(is_valid)

if __name__ == '__main__':
    unittest.main()
