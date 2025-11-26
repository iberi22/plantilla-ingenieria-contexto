"""
Repository Classifier - Production Readiness Detection

This module determines whether a repository is a production-ready project
or a tutorial/mock/example by analyzing multiple signals.
"""

import logging
import requests
from typing import Dict, Any, Optional
import re


class RepositoryClassifier:
    """
    Classifies repositories as production-ready, experimental, or tutorial/mock.

    Uses multiple signals:
    - Package adoption (npm, PyPI, Docker Hub downloads)
    - GitHub dependents
    - Contributors and commit patterns
    - Release history and semantic versioning
    - Documentation quality
    - Community engagement
    """

    def __init__(self, token: str):
        """
        Initialize RepositoryClassifier.

        Args:
            token: GitHub personal access token.
        """
        self.logger = logging.getLogger(__name__)
        self.token = token
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def classify(
        self,
        repo_data: Dict[str, Any],
        insights: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Classify a repository and calculate production readiness score.

        Args:
            repo_data: Basic repository data from GitHub API.
            insights: Optional insights data from InsightsCollector.

        Returns:
            Dictionary with classification and score.
        """
        try:
            score = 0
            signals = {}

            # Signal 1: Name/Description Analysis (0-10 points)
            name_score, name_signals = self._analyze_name_description(repo_data)
            score += name_score
            signals["name_analysis"] = name_signals

            # Signal 2: Package Adoption (0-30 points)
            adoption_score, adoption_data = self._check_package_adoption(repo_data)
            score += adoption_score
            signals["package_adoption"] = adoption_data

            # Signal 3: GitHub Dependents (0-15 points)
            dependents_score, dependents_data = self._check_dependents(repo_data)
            score += dependents_score
            signals["dependents"] = dependents_data

            # Signal 4: Contributors & Activity (0-20 points)
            if insights:
                activity_score, activity_data = self._analyze_activity(insights)
                score += activity_score
                signals["activity"] = activity_data

            # Signal 5: Release History (0-10 points)
            if insights:
                release_score, release_data = self._analyze_releases(insights)
                score += release_score
                signals["releases"] = release_data

            # Signal 6: Documentation Quality (0-10 points)
            docs_score, docs_data = self._analyze_documentation(repo_data)
            score += docs_score
            signals["documentation"] = docs_data

            # Signal 7: Community Health (0-5 points)
            if insights:
                community_score = insights.get("community", {}).get("health_percentage", 0) * 0.05
                score += community_score
                signals["community_health"] = community_score

            # Determine classification
            classification = self._classify_by_score(score, signals)

            return {
                "classification": classification,
                "production_score": round(score, 1),
                "signals": signals,
                "is_production_ready": score >= 60,
                "is_tutorial_mock": classification == "tutorial"
            }

        except Exception as e:
            self.logger.error(f"Classification failed: {e}")
            return {
                "classification": "unknown",
                "production_score": 0,
                "signals": {},
                "is_production_ready": False,
                "is_tutorial_mock": False
            }

    def _analyze_name_description(self, repo_data: Dict[str, Any]) -> tuple[float, Dict]:
        """Analyze repository name and description for tutorial indicators."""
        name = repo_data.get("name", "").lower()
        description = repo_data.get("description", "").lower()
        combined = f"{name} {description}"

        # Tutorial indicators (negative signals)
        tutorial_keywords = [
            "tutorial", "example", "demo", "starter", "template",
            "boilerplate", "sample", "learning", "course", "practice",
            "exercise", "playground", "sandbox", "hello-world"
        ]

        # Production indicators (positive signals)
        production_keywords = [
            "framework", "library", "tool", "platform", "engine",
            "system", "service", "api", "production", "enterprise"
        ]

        has_tutorial = any(kw in combined for kw in tutorial_keywords)
        has_production = any(kw in combined for kw in production_keywords)

        score = 10.0
        if has_tutorial:
            score = 0.0  # Strong negative signal
        elif has_production:
            score = 10.0
        else:
            score = 5.0

        return score, {
            "has_tutorial_keywords": has_tutorial,
            "has_production_keywords": has_production,
            "score": score
        }

    def _check_package_adoption(self, repo_data: Dict[str, Any]) -> tuple[float, Dict]:
        """Check package adoption on npm, PyPI, or Docker Hub."""
        repo_name = repo_data.get("name", "")
        language = repo_data.get("language", "").lower()

        adoption_data = {}
        score = 0.0

        # Check npm (for JavaScript/TypeScript projects)
        if language in ["javascript", "typescript"]:
            npm_data = self._check_npm_downloads(repo_name)
            adoption_data["npm"] = npm_data

            if npm_data.get("weekly_downloads", 0) > 10000:
                score += 30.0
            elif npm_data.get("weekly_downloads", 0) > 1000:
                score += 20.0
            elif npm_data.get("weekly_downloads", 0) > 100:
                score += 10.0

        # Check PyPI (for Python projects)
        elif language == "python":
            pypi_data = self._check_pypi_downloads(repo_name)
            adoption_data["pypi"] = pypi_data

            if pypi_data.get("monthly_downloads", 0) > 10000:
                score += 30.0
            elif pypi_data.get("monthly_downloads", 0) > 1000:
                score += 20.0
            elif pypi_data.get("monthly_downloads", 0) > 100:
                score += 10.0

        # Check Docker Hub
        docker_data = self._check_docker_pulls(repo_name)
        if docker_data.get("pull_count", 0) > 0:
            adoption_data["docker"] = docker_data

            if docker_data["pull_count"] > 10000:
                score += 15.0
            elif docker_data["pull_count"] > 1000:
                score += 10.0
            elif docker_data["pull_count"] > 100:
                score += 5.0

        # If no package found, check stars as proxy
        if score == 0:
            stars = repo_data.get("stargazers_count", 0)
            if stars > 5000:
                score = 15.0
            elif stars > 1000:
                score = 10.0
            elif stars > 500:
                score = 5.0

        return min(30.0, score), adoption_data

    def _check_npm_downloads(self, package_name: str) -> Dict[str, Any]:
        """Check npm download statistics."""
        try:
            # Normalize package name (GitHub repo name != npm package name often)
            # Try with @scope if it looks like a scoped package
            url = f"https://api.npmjs.org/downloads/point/last-week/{package_name}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    "exists": True,
                    "weekly_downloads": data.get("downloads", 0)
                }

            return {"exists": False, "weekly_downloads": 0}
        except Exception as e:
            self.logger.debug(f"NPM check failed for {package_name}: {e}")
            return {"exists": False, "weekly_downloads": 0}

    def _check_pypi_downloads(self, package_name: str) -> Dict[str, Any]:
        """Check PyPI download statistics."""
        try:
            # Normalize package name (replace - with _)
            normalized_name = package_name.replace("-", "_")

            # Check if package exists
            url = f"https://pypi.org/pypi/{normalized_name}/json"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                # PyPI doesn't provide download stats in API directly
                # We'd need pypistats.org API for accurate numbers
                # For now, check if package exists and is recent
                data = response.json()

                # Use pypistats API
                stats_url = f"https://pypistats.org/api/packages/{normalized_name}/recent"
                stats_response = requests.get(stats_url, timeout=5)

                downloads = 0
                if stats_response.status_code == 200:
                    stats = stats_response.json()
                    downloads = stats.get("data", {}).get("last_month", 0)

                return {
                    "exists": True,
                    "monthly_downloads": downloads
                }

            return {"exists": False, "monthly_downloads": 0}
        except Exception as e:
            self.logger.debug(f"PyPI check failed for {package_name}: {e}")
            return {"exists": False, "monthly_downloads": 0}

    def _check_docker_pulls(self, repo_name: str) -> Dict[str, Any]:
        """Check Docker Hub pull statistics."""
        try:
            # Try official Docker Hub API
            url = f"https://hub.docker.com/v2/repositories/library/{repo_name}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return {
                    "exists": True,
                    "pull_count": data.get("pull_count", 0)
                }

            return {"exists": False, "pull_count": 0}
        except Exception as e:
            self.logger.debug(f"Docker Hub check failed for {repo_name}: {e}")
            return {"exists": False, "pull_count": 0}

    def _check_dependents(self, repo_data: Dict[str, Any]) -> tuple[float, Dict]:
        """Check GitHub dependents count (requires scraping or GraphQL)."""
        # Note: GitHub's REST API doesn't provide dependents count directly
        # Would need GraphQL API or web scraping
        # For now, use stars as a proxy

        full_name = repo_data.get("full_name", "")

        try:
            # Try to fetch from dependency graph (requires GraphQL)
            # Simplified: use forks + watchers as proxy
            forks = repo_data.get("forks_count", 0)
            watchers = repo_data.get("watchers_count", 0)

            # Estimate dependents from these metrics
            estimated_dependents = (forks + watchers) // 10

            score = 0.0
            if estimated_dependents > 50:
                score = 15.0
            elif estimated_dependents > 20:
                score = 10.0
            elif estimated_dependents > 10:
                score = 5.0

            return score, {
                "estimated_dependents": estimated_dependents,
                "forks": forks,
                "watchers": watchers
            }
        except Exception as e:
            self.logger.warning(f"Dependents check failed: {e}")
            return 0.0, {}

    def _analyze_activity(self, insights: Dict[str, Any]) -> tuple[float, Dict]:
        """Analyze repository activity patterns."""
        score = 0.0
        data = {}

        # Contributors (0-10 points)
        contributors = insights.get("contributors", {})
        contributor_count = contributors.get("count", 0)

        if contributor_count > 10:
            score += 10.0
        elif contributor_count > 5:
            score += 7.0
        elif contributor_count > 2:
            score += 4.0
        elif contributor_count == 1:
            score += 0.0  # Single contributor = tutorial risk

        data["contributor_count"] = contributor_count

        # Commit frequency (0-10 points)
        commit_activity = insights.get("commit_activity", {})
        weekly_avg = commit_activity.get("weekly_average", 0)

        if weekly_avg > 10:
            score += 10.0
        elif weekly_avg > 5:
            score += 7.0
        elif weekly_avg > 1:
            score += 4.0

        data["weekly_commits"] = weekly_avg
        data["is_active"] = commit_activity.get("is_active", False)

        return score, data

    def _analyze_releases(self, insights: Dict[str, Any]) -> tuple[float, Dict]:
        """Analyze release history."""
        score = 0.0
        releases = insights.get("releases", {})

        release_count = releases.get("count", 0)
        has_semver = releases.get("has_semantic_versioning", False)
        recent_count = releases.get("recent_count", 0)

        # Has releases (0-5 points)
        if release_count > 10:
            score += 5.0
        elif release_count > 5:
            score += 4.0
        elif release_count > 0:
            score += 2.0

        # Semantic versioning (0-3 points)
        if has_semver:
            score += 3.0

        # Recent releases (0-2 points)
        if recent_count > 3:
            score += 2.0
        elif recent_count > 0:
            score += 1.0

        return score, {
            "total_releases": release_count,
            "recent_releases": recent_count,
            "has_semantic_versioning": has_semver,
            "score": score
        }

    def _analyze_documentation(self, repo_data: Dict[str, Any]) -> tuple[float, Dict]:
        """Analyze documentation quality."""
        score = 0.0
        data = {}

        # Has wiki (0-2 points)
        if repo_data.get("has_wiki"):
            score += 2.0
            data["has_wiki"] = True

        # Has pages (0-3 points)
        if repo_data.get("has_pages"):
            score += 3.0
            data["has_pages"] = True

        # README length estimation from size (0-5 points)
        size_kb = repo_data.get("size", 0)
        if size_kb > 1000:  # Large repo with substantial content
            score += 5.0
        elif size_kb > 100:
            score += 3.0
        elif size_kb > 10:
            score += 1.0

        data["repo_size_kb"] = size_kb

        return score, data

    def _classify_by_score(self, score: float, signals: Dict) -> str:
        """Classify repository based on production readiness score."""
        # Override: if name analysis detected tutorial keywords
        name_analysis = signals.get("name_analysis", {})
        if name_analysis.get("has_tutorial_keywords"):
            return "tutorial"

        # Score-based classification
        if score >= 80:
            return "production"  # Production-ready, widely adopted
        elif score >= 60:
            return "stable"  # Stable, moderate adoption
        elif score >= 40:
            return "experimental"  # Early stage, some adoption
        elif score >= 20:
            return "hobby"  # Hobby project, minimal adoption
        else:
            return "tutorial"  # Tutorial/mock/abandoned
