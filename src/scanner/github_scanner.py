import requests
import datetime
import os
import logging
from typing import List, Dict, Any, Optional

try:
    from .insights_collector import InsightsCollector
    from .repo_classifier import RepoClassifier
except ImportError:
    # Fallback for when running scripts from different cwd
    from src.scanner.insights_collector import InsightsCollector
    from src.scanner.repo_classifier import RepoClassifier

class GitHubScanner:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_url = "https://api.github.com"
        self.logger = logging.getLogger(__name__)

        # Initialize helpers
        self.insights_collector = InsightsCollector(token)
        self.classifier = RepoClassifier()

    def scan_recent_repos(self, query="created:>2023-01-01", limit=10) -> List[Dict[str, Any]]:
        """
        Scans for recent repositories and filters them using enhanced analysis.

        Returns:
            List of filtered and enriched repository data.
        """
        # In a real scenario, we would calculate the timestamp for "last hour"
        # one_hour_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat()
        # query = f"created:>{one_hour_ago} {query}"

        url = f"{self.api_url}/search/repositories?q={query}&sort=updated&order=desc&per_page={limit * 2}" # Fetch more to allow filtering
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            self.logger.error(f"Error searching repos: {response.text}")
            return []

        items = response.json().get("items", [])
        results = []

        for repo in items:
            # 1. Basic Validation (Cheap)
            if not self.validate_repo_basic(repo):
                continue

            # 2. Enhanced Analysis (Expensive)
            try:
                insights = self.insights_collector.collect_insights(repo["full_name"])
                classification = self.classifier.classify_repo(repo, insights)

                if classification["is_real_project"]:
                    # Merge data
                    enriched_repo = repo.copy()
                    enriched_repo["insights"] = insights
                    enriched_repo["analysis"] = classification
                    results.append(enriched_repo)
                    self.logger.info(f"✅ Accepted {repo['full_name']} (Score: {classification['score']})")
                else:
                    self.logger.info(f"❌ Rejected {repo['full_name']} (Score: {classification['score']}). Reasons: {classification['reasons']}")
            except Exception as e:
                self.logger.error(f"Error analyzing {repo['full_name']}: {e}")
                continue

            if len(results) >= limit:
                break

        return results

    def validate_repo_basic(self, repo):
        """
        Performs cheap, basic validation to filter out obvious garbage.
        """
        # 1. Basic Metadata Checks
        if not repo.get("description") or len(repo["description"]) < 10:
            self.logger.debug(f"Skipping {repo['full_name']}: Description too short or missing.")
            return False

        if not repo.get("license"):
            # License is a strong signal, but maybe not strictly required for 'basic' check?
            # Let's keep it required as per original logic.
            self.logger.debug(f"Skipping {repo['full_name']}: No license found.")
            return False

        if repo.get("archived") or repo.get("disabled"):
            return False

        # 2. Keyword Filtering (Exclude toy projects)
        name_desc = (repo["name"] + " " + (repo["description"] or "")).lower()
        exclude_keywords = ["alpha", "test", "demo", "example", "tutorial", "course", "starter", "template"]
        if any(k in name_desc for k in exclude_keywords):
            # Exception for "beta" if it looks solid otherwise
            if "beta" not in name_desc:
                self.logger.debug(f"Skipping {repo['full_name']}: Contains exclude keywords.")
                return False

        return True

    # Legacy method kept for backward compatibility if needed, but updated to use basic
    def validate_repo(self, repo):
        return self.validate_repo_basic(repo)

    def _has_substantial_readme(self, repo_full_name):
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/readme"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # size is in bytes. Let's require at least 500 bytes of documentation.
                return data.get("size", 0) > 500
            return False
        except Exception:
            return False

    def _check_ci_status(self, repo_full_name):
        # Check for successful workflow runs in the last 24 hours
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/actions/runs?per_page=5&status=success"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                runs = response.json().get("workflow_runs", [])
                return len(runs) > 0
            return False
        except Exception:
            return False

    def get_latest_commit(self, repo_full_name: str):
        """Fetches the latest commit hash for the default branch."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/commits/HEAD"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.json()["sha"]
            return None
        except Exception as e:
            self.logger.error(f"Error fetching commit for {repo_full_name}: {e}")
            return None
