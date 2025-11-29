import pytest
from unittest.mock import patch, MagicMock
from src.scanner.github_scanner import GitHubScanner

class TestGitHubScanner:

    @pytest.fixture
    def scanner(self):
        return GitHubScanner(token="mock_token")

    @patch("src.scanner.github_scanner.requests.get")
    def test_scan_recent_repos_success(self, mock_get, scanner):
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"name": "repo1", "full_name": "user/repo1", "description": "A valid project description", "license": {"key": "mit"}, "archived": False, "disabled": False},
                {"name": "repo2", "full_name": "user/repo2", "description": "Another valid project", "license": {"key": "apache-2.0"}, "archived": False, "disabled": False}
            ]
        }
        mock_get.return_value = mock_response

        # Mock the enhanced analysis methods to avoid API calls
        with patch.object(scanner, 'validate_repo_basic', return_value=True), \
             patch.object(scanner.insights_collector, 'collect_insights', return_value={}), \
             patch.object(scanner.classifier, 'classify_repo', return_value={'is_real_project': True, 'score': 80, 'reasons': []}):
            repos = scanner.scan_recent_repos(limit=2)

            assert len(repos) == 2
            assert repos[0]["name"] == "repo1"
            mock_get.assert_called_once()

    @patch("src.scanner.github_scanner.requests.get")
    def test_scan_recent_repos_failure(self, mock_get, scanner):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Rate Limit Exceeded"
        mock_get.return_value = mock_response

        repos = scanner.scan_recent_repos()

        assert len(repos) == 0

    def test_validate_repo_basic_checks(self, scanner):
        # Valid repo
        good_repo = {
            "full_name": "user/good",
            "description": "A very good project with long description",
            "license": {"key": "mit"},
            "archived": False,
            "disabled": False,
            "name": "good-project"
        }

        # We need to mock the internal checks _has_substantial_readme and _check_ci_status
        # Since they are private methods calling APIs, we should mock them or the requests they make.
        # For this unit test, let's mock the methods directly on the instance.

        with patch.object(scanner, '_has_substantial_readme', return_value=True), \
             patch.object(scanner, '_check_ci_status', return_value=True):
            assert scanner.validate_repo(good_repo) is True

    def test_validate_repo_bad_description(self, scanner):
        bad_repo = {
            "full_name": "user/bad",
            "description": "Short",
            "license": {"key": "mit"},
            "name": "bad"
        }
        assert scanner.validate_repo(bad_repo) is False
