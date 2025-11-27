import requests
import logging
from typing import Dict, Any, Optional

class InsightsCollector:
    """
    Collects advanced metrics and insights from GitHub repositories.
    """

    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_url = "https://api.github.com"
        self.logger = logging.getLogger(__name__)

    def collect_insights(self, repo_full_name: str) -> Dict[str, Any]:
        """
        Collects comprehensive insights for a repository.
        """
        self.logger.info(f"Collecting insights for {repo_full_name}")

        insights = {
            "contributors_count": self._get_contributors_count(repo_full_name),
            "commit_frequency_score": self._get_commit_activity(repo_full_name),
            "health_percentage": self._get_community_health(repo_full_name),
            "pr_merge_ratio": self._get_pr_merge_ratio(repo_full_name)
        }

        return insights

    def _get_contributors_count(self, repo_full_name: str) -> int:
        """Get the number of contributors (capped at 100 per page usually)."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/contributors?per_page=1&anon=true"
            # Using link header method would be accurate but slow.
            # For efficiency, we can just check page 1 size or use the Link header.
            # GitHub API doesn't give total count directly in body.
            # Faster way: check page 1.
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                # Check Link header for last page
                if "Link" in response.headers:
                    links = response.headers["Link"]
                    # parse last page number
                    # <...&page=5>; rel="last"
                    try:
                        last_page = int(links.split('rel="last"')[0].split('page=')[-1].strip('>; '))
                        return last_page
                    except:
                        return 1 # Fallback
                return len(response.json()) # Should be 1 if per_page=1
            return 0
        except Exception as e:
            self.logger.warning(f"Failed to get contributors: {e}")
            return 0

    def _get_commit_activity(self, repo_full_name: str) -> float:
        """
        Get commit activity score (0-10) based on weekly participation.
        """
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/stats/participation"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "all" in data:
                    # Sum last 4 weeks
                    recent_commits = sum(data["all"][-4:])
                    # Normalize: if > 20 commits in last month, high score
                    score = min(recent_commits / 2, 10.0) # 20 commits -> 10 points
                    return round(score, 1)
            return 0.0
        except Exception:
            return 0.0

    def _get_community_health(self, repo_full_name: str) -> int:
        """Get community profile health percentage."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/community/profile"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("health_percentage", 0)
            return 0
        except Exception:
            return 0

    def _get_pr_merge_ratio(self, repo_full_name: str) -> float:
        """
        Calculate ratio of merged PRs to closed PRs (last 100).
        """
        try:
            # We want closed PRs
            url = f"{self.api_url}/repos/{repo_full_name}/pulls?state=closed&per_page=100"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                prs = response.json()
                if not prs:
                    return 0.0

                merged_count = sum(1 for pr in prs if pr.get("merged_at") is not None)
                total_closed = len(prs)

                return round(merged_count / total_closed, 2)
            return 0.0
        except Exception:
            return 0.0
