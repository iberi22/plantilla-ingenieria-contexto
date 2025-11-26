import requests
import datetime
import os
import logging

class GitHubScanner:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_url = "https://api.github.com"

    def scan_recent_repos(self, query="created:>2023-01-01", limit=10):
        # In a real scenario, we would calculate the timestamp for "last hour"
        # one_hour_ago = (datetime.datetime.utcnow() - datetime.timedelta(hours=1)).isoformat()
        # query = f"created:>{one_hour_ago} {query}"

        url = f"{self.api_url}/search/repositories?q={query}&sort=updated&order=desc&per_page={limit}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            logging.error(f"Error searching repos: {response.text}")
            return []

        return response.json().get("items", [])

    def validate_repo(self, repo):
        # 1. Basic Metadata Checks
        if not repo.get("description") or len(repo["description"]) < 20:
            logging.info(f"Skipping {repo['full_name']}: Description too short or missing.")
            return False

        if not repo.get("license"):
            logging.info(f"Skipping {repo['full_name']}: No license found.")
            return False

        if repo.get("archived") or repo.get("disabled"):
            return False

        # 2. Keyword Filtering (Exclude toy projects)
        name_desc = (repo["name"] + " " + (repo["description"] or "")).lower()
        exclude_keywords = ["alpha", "test", "demo", "example", "tutorial", "course", "starter", "template"]
        if any(k in name_desc for k in exclude_keywords):
            # Exception for "beta" if it looks solid otherwise, but generally avoid alpha/test
            if "beta" not in name_desc:
                logging.info(f"Skipping {repo['full_name']}: Contains exclude keywords.")
                return False

        # 3. Activity Check (Must be active recently)
        # pushed_at is ISO 8601
        # We could parse it, but for now let's trust the search query 'created:>...' handles recency.

        # 4. Content Quality (Readme & CI)
        # Check if Readme exists and is substantial
        if not self._has_substantial_readme(repo["full_name"]):
            logging.info(f"Skipping {repo['full_name']}: Readme too short.")
            return False

        # 5. CI Status (The "Gold Standard" for quality)
        # Only check CI if everything else passes, to save API calls
        if not self._check_ci_status(repo["full_name"]):
            logging.info(f"Skipping {repo['full_name']}: CI not passing or not found.")
            return False

        return True

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
            logging.error(f"Error fetching commit for {repo_full_name}: {e}")
            return None
