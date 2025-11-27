import unittest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scanner.github_scanner import GitHubScanner
from scanner.insights_collector import InsightsCollector
from scanner.repo_classifier import RepoClassifier

class TestScannerEnhanced(unittest.TestCase):
    def setUp(self):
        self.token = "fake_token"
        self.scanner = GitHubScanner(self.token)

    @patch("scanner.github_scanner.requests.get")
    def test_scan_recent_repos_flow(self, mock_get):
        # Mock search response
        mock_search_resp = MagicMock()
        mock_search_resp.status_code = 200
        mock_search_resp.json.return_value = {
            "items": [
                {
                    "full_name": "owner/good-repo",
                    "name": "good-repo",
                    "description": "A very good python project with lots of stars.",
                    "stargazers_count": 500,
                    "license": {"name": "MIT"},
                    "archived": False,
                    "disabled": False,
                    "topics": ["python", "ai"]
                },
                {
                    "full_name": "owner/bad-repo",
                    "name": "bad-repo",
                    "description": "demo",
                    "stargazers_count": 0,
                    "license": None, # Fails basic
                    "archived": False
                }
            ]
        }

        # Mock insights responses
        # We need to handle multiple calls to requests.get
        # 1. Search (handled above, but logic uses side_effect usually)
        # 2. Contributors
        # 3. Stats
        # 4. Community
        # 5. Pulls

        def side_effect(url, headers):
            if "search/repositories" in url:
                return mock_search_resp
            elif "contributors" in url:
                m = MagicMock()
                m.status_code = 200
                m.json.return_value = [{"login": "user1"}, {"login": "user2"}] # 2 contributors
                return m
            elif "stats/participation" in url:
                m = MagicMock()
                m.status_code = 200
                m.json.return_value = {"all": [10, 10, 10, 10]} # Active
                return m
            elif "community/profile" in url:
                m = MagicMock()
                m.status_code = 200
                m.json.return_value = {"health_percentage": 100}
                return m
            elif "pulls" in url:
                m = MagicMock()
                m.status_code = 200
                # 1 merged, 1 closed
                m.json.return_value = [
                    {"merged_at": "2024-01-01"},
                    {"merged_at": None}
                ]
                return m
            elif "readme" in url:
                 m = MagicMock()
                 m.status_code = 200
                 m.json.return_value = {"size": 1000}
                 return m
            elif "actions/runs" in url:
                 m = MagicMock()
                 m.status_code = 200
                 m.json.return_value = {"workflow_runs": [{}]}
                 return m
            return MagicMock(status_code=404)

        mock_get.side_effect = side_effect

        # Run scan
        repos = self.scanner.scan_recent_repos(limit=2)

        # 'bad-repo' should be filtered by validate_repo_basic (no license, desc 'demo')
        # 'good-repo' should pass basic, get insights, and pass classifier

        self.assertEqual(len(repos), 1)
        good = repos[0]
        self.assertEqual(good["name"], "good-repo")
        self.assertIn("insights", good)
        self.assertIn("analysis", good)

        # Check insights
        self.assertEqual(good["insights"]["contributors_count"], 2)
        self.assertEqual(good["insights"]["health_percentage"], 100)

        # Check analysis
        self.assertTrue(good["analysis"]["is_real_project"])
        self.assertGreater(good["analysis"]["score"], 60)

    def test_classifier_logic(self):
        classifier = RepoClassifier()

        # Real repo case
        repo_data = {
            "name": "react",
            "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces.",
            "stargazers_count": 200000,
            "license": "MIT",
            "topics": ["javascript", "ui"]
        }
        insights = {
            "contributors_count": 100,
            "commit_frequency_score": 10.0,
            "health_percentage": 90,
            "pr_merge_ratio": 0.8
        }

        result = classifier.classify_repo(repo_data, insights)
        self.assertTrue(result["is_real_project"])
        self.assertEqual(result["score"], 100) # Should be maxed out

        # Fake repo case
        repo_data_fake = {
            "name": "react-demo",
            "description": "simple demo",
            "stargazers_count": 2,
            "license": "MIT"
        }
        insights_fake = {
            "contributors_count": 1,
            "commit_frequency_score": 0.0,
            "health_percentage": 0
        }

        result_fake = classifier.classify_repo(repo_data_fake, insights_fake)
        self.assertFalse(result_fake["is_real_project"])
        self.assertLess(result_fake["score"], 60)
        self.assertIn("Contains negative keyword: demo", result_fake["reasons"])

if __name__ == '__main__':
    unittest.main()
