"""
GitHub Insights Collector - Advanced Repository Metrics

This module collects advanced metrics from GitHub's APIs to provide
deep insights into repository health, activity, and production readiness.
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import statistics


class InsightsCollector:
    """
    Collects advanced metrics from GitHub repositories using multiple APIs.

    Metrics collected:
    - Contributors count and activity
    - Commit frequency and patterns
    - Issue velocity and response time
    - PR merge rate and review time
    - Release frequency
    - Community health score
    - Code frequency (additions/deletions per week)
    - Participation stats
    """

    def __init__(self, token: str):
        """
        Initialize InsightsCollector.

        Args:
            token: GitHub personal access token with repo scope.
        """
        self.logger = logging.getLogger(__name__)
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.api_url = "https://api.github.com"

    def collect_insights(self, repo_full_name: str) -> Dict[str, Any]:
        """
        Collect all available insights for a repository.

        Args:
            repo_full_name: Full repository name (owner/repo).

        Returns:
            Dictionary with all collected metrics.
        """
        insights = {}

        try:
            # Contributors metrics
            insights["contributors"] = self._get_contributors_insights(repo_full_name)

            # Commit activity
            insights["commit_activity"] = self._get_commit_activity(repo_full_name)

            # Issue metrics
            insights["issues"] = self._get_issue_metrics(repo_full_name)

            # PR metrics
            insights["pull_requests"] = self._get_pr_metrics(repo_full_name)

            # Release metrics
            insights["releases"] = self._get_release_metrics(repo_full_name)

            # Community health
            insights["community"] = self._get_community_health(repo_full_name)

            # Participation stats
            insights["participation"] = self._get_participation_stats(repo_full_name)

            self.logger.info(f"Collected insights for {repo_full_name}")
            return insights

        except Exception as e:
            self.logger.error(f"Failed to collect insights for {repo_full_name}: {e}")
            return {}

    def _get_contributors_insights(self, repo_full_name: str) -> Dict[str, Any]:
        """Get contributor statistics."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/contributors"
            response = requests.get(url, headers=self.headers, params={"per_page": 100})

            if response.status_code != 200:
                return {"count": 0, "top_contributors": []}

            contributors = response.json()

            return {
                "count": len(contributors),
                "top_contributors": [
                    {
                        "login": c["login"],
                        "contributions": c["contributions"]
                    }
                    for c in contributors[:5]
                ],
                "has_diverse_contributors": len(contributors) > 5
            }
        except Exception as e:
            self.logger.warning(f"Failed to get contributors: {e}")
            return {"count": 0}

    def _get_commit_activity(self, repo_full_name: str) -> Dict[str, Any]:
        """Get commit activity over the last year."""
        try:
            # Get commit activity (last 52 weeks)
            url = f"{self.api_url}/repos/{repo_full_name}/stats/commit_activity"
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                return {"weekly_average": 0, "last_month_commits": 0}

            activity = response.json()

            if not activity:
                return {"weekly_average": 0, "last_month_commits": 0}

            # Calculate weekly average
            weekly_commits = [week["total"] for week in activity]
            weekly_avg = statistics.mean(weekly_commits) if weekly_commits else 0

            # Last month (4 weeks)
            last_month = sum(weekly_commits[-4:]) if len(weekly_commits) >= 4 else 0

            return {
                "weekly_average": round(weekly_avg, 2),
                "last_month_commits": last_month,
                "is_active": last_month > 0,
                "trend": "increasing" if weekly_commits[-4:] > weekly_commits[-8:-4] else "stable"
            }
        except Exception as e:
            self.logger.warning(f"Failed to get commit activity: {e}")
            return {"weekly_average": 0}

    def _get_issue_metrics(self, repo_full_name: str) -> Dict[str, Any]:
        """Get issue statistics and velocity."""
        try:
            # Get recent issues (last 30 days)
            since = (datetime.now() - timedelta(days=30)).isoformat()

            # Open issues
            open_url = f"{self.api_url}/repos/{repo_full_name}/issues"
            open_response = requests.get(
                open_url,
                headers=self.headers,
                params={"state": "open", "per_page": 100}
            )

            # Closed issues
            closed_url = f"{self.api_url}/repos/{repo_full_name}/issues"
            closed_response = requests.get(
                closed_url,
                headers=self.headers,
                params={"state": "closed", "since": since, "per_page": 100}
            )

            if open_response.status_code != 200 or closed_response.status_code != 200:
                return {"open_count": 0, "closed_last_month": 0}

            open_issues = open_response.json()
            closed_issues = closed_response.json()

            # Filter out PRs (issues endpoint includes PRs)
            open_issues = [i for i in open_issues if "pull_request" not in i]
            closed_issues = [i for i in closed_issues if "pull_request" not in i]

            # Calculate response time for closed issues
            response_times = []
            for issue in closed_issues[:10]:  # Sample 10 recent
                created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
                closed = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
                response_times.append((closed - created).days)

            avg_response = statistics.mean(response_times) if response_times else 0

            return {
                "open_count": len(open_issues),
                "closed_last_month": len(closed_issues),
                "avg_response_days": round(avg_response, 1),
                "velocity": len(closed_issues),  # Issues closed in 30 days
                "has_critical": any("critical" in str(i.get("labels", [])).lower() for i in open_issues)
            }
        except Exception as e:
            self.logger.warning(f"Failed to get issue metrics: {e}")
            return {"open_count": 0}

    def _get_pr_metrics(self, repo_full_name: str) -> Dict[str, Any]:
        """Get pull request statistics."""
        try:
            # Recent PRs (last 30 days)
            since = (datetime.now() - timedelta(days=30)).isoformat()

            url = f"{self.api_url}/repos/{repo_full_name}/pulls"
            response = requests.get(
                url,
                headers=self.headers,
                params={"state": "closed", "per_page": 100}
            )

            if response.status_code != 200:
                return {"merged_last_month": 0, "merge_rate": 0}

            prs = response.json()

            # Filter to last 30 days
            recent_prs = [
                pr for pr in prs
                if datetime.fromisoformat(pr["closed_at"].replace("Z", "+00:00")) > datetime.now() - timedelta(days=30)
            ]

            merged_prs = [pr for pr in recent_prs if pr.get("merged_at")]

            merge_rate = (len(merged_prs) / len(recent_prs) * 100) if recent_prs else 0

            return {
                "merged_last_month": len(merged_prs),
                "total_closed_last_month": len(recent_prs),
                "merge_rate": round(merge_rate, 1),
                "has_external_contributors": any(
                    pr["user"]["login"] != pr.get("base", {}).get("repo", {}).get("owner", {}).get("login")
                    for pr in merged_prs[:10]
                )
            }
        except Exception as e:
            self.logger.warning(f"Failed to get PR metrics: {e}")
            return {"merged_last_month": 0}

    def _get_release_metrics(self, repo_full_name: str) -> Dict[str, Any]:
        """Get release statistics."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/releases"
            response = requests.get(url, headers=self.headers, params={"per_page": 50})

            if response.status_code != 200:
                return {"count": 0, "latest_version": None}

            releases = response.json()

            if not releases:
                return {"count": 0, "latest_version": None}

            # Filter releases in last year
            one_year_ago = datetime.now() - timedelta(days=365)
            recent_releases = [
                r for r in releases
                if datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")) > one_year_ago
            ]

            return {
                "count": len(releases),
                "recent_count": len(recent_releases),
                "latest_version": releases[0]["tag_name"],
                "latest_date": releases[0]["published_at"],
                "has_semantic_versioning": any(
                    r["tag_name"].startswith("v") or r["tag_name"][0].isdigit()
                    for r in releases
                )
            }
        except Exception as e:
            self.logger.warning(f"Failed to get release metrics: {e}")
            return {"count": 0}

    def _get_community_health(self, repo_full_name: str) -> Dict[str, Any]:
        """Get community health metrics."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/community/profile"
            response = requests.get(
                url,
                headers={**self.headers, "Accept": "application/vnd.github.v3+json"}
            )

            if response.status_code != 200:
                return {"health_percentage": 0}

            data = response.json()

            return {
                "health_percentage": data.get("health_percentage", 0),
                "has_code_of_conduct": data.get("files", {}).get("code_of_conduct") is not None,
                "has_contributing": data.get("files", {}).get("contributing") is not None,
                "has_license": data.get("files", {}).get("license") is not None,
                "has_readme": data.get("files", {}).get("readme") is not None
            }
        except Exception as e:
            self.logger.warning(f"Failed to get community health: {e}")
            return {"health_percentage": 0}

    def _get_participation_stats(self, repo_full_name: str) -> Dict[str, Any]:
        """Get participation statistics (owner vs all)."""
        try:
            url = f"{self.api_url}/repos/{repo_full_name}/stats/participation"
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                return {"owner_percentage": 100}

            data = response.json()

            all_commits = sum(data.get("all", []))
            owner_commits = sum(data.get("owner", []))

            owner_percentage = (owner_commits / all_commits * 100) if all_commits > 0 else 100

            return {
                "owner_percentage": round(owner_percentage, 1),
                "is_collaborative": owner_percentage < 80
            }
        except Exception as e:
            self.logger.warning(f"Failed to get participation stats: {e}")
            return {"owner_percentage": 100}

    def calculate_activity_score(self, insights: Dict[str, Any]) -> int:
        """
        Calculate overall activity score (0-100).

        Args:
            insights: Dictionary of collected insights.

        Returns:
            Activity score from 0 to 100.
        """
        score = 0

        # Commit activity (25 points)
        weekly_avg = insights.get("commit_activity", {}).get("weekly_average", 0)
        score += min(25, weekly_avg * 2)

        # Contributors (20 points)
        contributor_count = insights.get("contributors", {}).get("count", 0)
        score += min(20, contributor_count * 2)

        # Issue velocity (20 points)
        velocity = insights.get("issues", {}).get("velocity", 0)
        score += min(20, velocity / 2)

        # PR activity (20 points)
        prs = insights.get("pull_requests", {}).get("merged_last_month", 0)
        score += min(20, prs * 2)

        # Community health (15 points)
        health = insights.get("community", {}).get("health_percentage", 0)
        score += health * 0.15

        return min(100, round(score))
